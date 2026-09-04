from __future__ import annotations

import base64
from pathlib import Path
import uuid
from typing import Any

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .logging_utils import RequestLogger
from .prompts import ALLOWED_PEOPLE_COUNTS, SCENARIO_IDS, build_image_generation_prompt
from .schemas import (
    GenerationError,
    GenerationErrorResponse,
    GenerationSuccessResponse,
    HealthResponse,
    LogLevel,
)
from .services.image_generation import (
    ALLOWED_MIME_TYPES,
    ImageGenerationService,
    ProviderError,
    detect_raster_mime,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

settings = get_settings()
image_service = ImageGenerationService(settings)
app = FastAPI(title="Century Ply AI Photobooth API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


def _error_response(
    *,
    request_id: str,
    logger: RequestLogger,
    code: str,
    message: str,
    status_code: int,
    retryable: bool,
    level: LogLevel = "warning",
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    logger.add(level, "generation_failed", message, {"code": code, **(details or {})})
    payload = GenerationErrorResponse(
        request_id=request_id,
        error=GenerationError(code=code, message=message, retryable=retryable),
        logs=logger.entries(),
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump(mode="json"))


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(model=settings.image_model)


@app.post("/api/generate")
async def generate(
    people_count: int = Form(...),
    scenario_id: str = Form(...),
    image: UploadFile | None = File(default=None),
) -> JSONResponse:
    """Validate one client-checked portrait and send exactly one provider request."""

    request_id = str(uuid.uuid4())
    logger = RequestLogger()
    logger.add("info", "request_received", "Generation request received.", {"request_id": request_id})

    if people_count not in ALLOWED_PEOPLE_COUNTS:
        return _error_response(
            request_id=request_id,
            logger=logger,
            code="PEOPLE_COUNT_INVALID",
            message="Choose 1, 2, 3, or 4 people.",
            status_code=400,
            retryable=False,
            details={"people_count": people_count},
        )

    normalized_scenario_id = scenario_id.strip().lower()
    if normalized_scenario_id not in SCENARIO_IDS:
        return _error_response(
            request_id=request_id,
            logger=logger,
            code="SCENARIO_INVALID",
            message="Choose a valid Vietnamese scenario.",
            status_code=400,
            retryable=False,
            details={"scenario_id": normalized_scenario_id or "unknown"},
        )

    if image is None:
        return _error_response(
            request_id=request_id,
            logger=logger,
            code="IMAGE_REQUIRED",
            message="Choose a photo to continue.",
            status_code=400,
            retryable=False,
        )

    mime_type = (image.content_type or "").lower()
    if mime_type not in ALLOWED_MIME_TYPES:
        return _error_response(
            request_id=request_id,
            logger=logger,
            code="IMAGE_UNSUPPORTED_TYPE",
            message="Please choose a JPEG, PNG, or WebP image.",
            status_code=400,
            retryable=False,
            details={"mime_type": mime_type or "unknown"},
        )

    try:
        image_bytes = await image.read(settings.max_upload_bytes + 1)
    finally:
        await image.close()

    if not image_bytes:
        return _error_response(
            request_id=request_id,
            logger=logger,
            code="IMAGE_EMPTY",
            message="That image is empty. Please choose another photo.",
            status_code=400,
            retryable=False,
        )
    if len(image_bytes) > settings.max_upload_bytes:
        return _error_response(
            request_id=request_id,
            logger=logger,
            code="IMAGE_TOO_LARGE",
            message="That image is larger than 10 MB. Please choose a smaller photo.",
            status_code=413,
            retryable=False,
            details={"byte_count": len(image_bytes)},
        )
    if detect_raster_mime(image_bytes) != mime_type:
        return _error_response(
            request_id=request_id,
            logger=logger,
            code="IMAGE_INVALID_CONTENT",
            message="That file is not a valid image. Please choose another photo.",
            status_code=400,
            retryable=False,
            details={"mime_type": mime_type},
        )

    generation_prompt = build_image_generation_prompt(people_count, normalized_scenario_id)
    logger.add(
        "info",
        "input_validated",
        "Photo, people count, and scenario passed validation.",
        {
            "mime_type": mime_type,
            "byte_count": len(image_bytes),
            "people_count": people_count,
            "scenario_id": normalized_scenario_id,
        },
    )
    logger.add(
        "info",
        "provider_request",
        "Sending the portrait to the image service.",
        {
            "model": settings.image_model,
            "people_count": people_count,
            "scenario_id": normalized_scenario_id,
            "aspect_ratio": "3:4",
            "max_tokens": 4096,
        },
    )

    try:
        result = await image_service.generate_image(
            image_bytes=image_bytes,
            mime_type=mime_type,
            prompt=generation_prompt,
            request_id=request_id,
        )
    except ProviderError as exc:
        return _error_response(
            request_id=request_id,
            logger=logger,
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            retryable=exc.retryable,
            level="error",
            details={"http_status": exc.http_status, "latency_ms": exc.latency_ms},
        )
    except Exception:
        return _error_response(
            request_id=request_id,
            logger=logger,
            code="GENERATION_FAILED",
            message="The image service had a temporary problem.",
            status_code=502,
            retryable=True,
            level="error",
        )

    logger.add(
        "info",
        "provider_response",
        "The image service returned an image.",
        {
            "http_status": result.http_status,
            "latency_ms": result.latency_ms,
            "output_mime_type": result.mime_type,
            "output_size_bytes": len(result.image_bytes),
        },
    )
    logger.add(
        "success",
        "generation_completed",
        "Portrait generation completed.",
        {"http_status": result.http_status, "latency_ms": result.latency_ms},
    )
    result_image = f"data:{result.mime_type};base64,{base64.b64encode(result.image_bytes).decode('ascii')}"
    payload = GenerationSuccessResponse(request_id=request_id, result_image=result_image, logs=logger.entries())
    return JSONResponse(status_code=200, content=payload.model_dump(mode="json"))


if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
