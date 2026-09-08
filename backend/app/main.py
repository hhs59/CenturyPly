from __future__ import annotations

import base64
from pathlib import Path
import time
import uuid
import asyncio
import logging
from contextlib import asynccontextmanager, suppress
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from starlette.concurrency import run_in_threadpool

from .config import get_settings
from .dashboard_store import DashboardStore
from .photo_api import PhotoService, create_photo_router
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
dashboard_store = DashboardStore(settings.dashboard_data_dir, settings.dashboard_timezone)
photo_service = PhotoService(settings)


@asynccontextmanager
async def lifespan(_app):
    async def cleanup_photos():
        while True:
            try:
                await run_in_threadpool(photo_service.cleanup)
            except Exception:
                logging.getLogger(__name__).exception("QR photo cleanup failed")
            await asyncio.sleep(3600)
    task = asyncio.create_task(cleanup_photos())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


app = FastAPI(title="Century Ply AI Photobooth API", version="0.1.0", lifespan=lifespan)
app.include_router(create_photo_router(photo_service))

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


@app.get("/api/dashboard/overview")
def dashboard_overview() -> dict[str, Any]:
    result = dashboard_store.overview()
    result["total_downloads"] = sum(_qr_counts().values())
    return result


def _qr_counts():
    try:
        return photo_service.store.counts()
    except Exception:
        logging.getLogger(__name__).exception("QR download metrics unavailable")
        return {}


@app.get("/api/dashboard/sessions")
def dashboard_sessions(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50_000),
    search: str = Query(default="", max_length=200),
    scenario_id: str = Query(default="", max_length=80),
    status: str = Query(default="", max_length=20),
) -> dict[str, Any]:
    result = dashboard_store.list_sessions(
        page=page,
        limit=limit,
        search=search,
        scenario_id=scenario_id,
        status=status,
    )
    counts = _qr_counts()
    for session in result["data"]:
        session["download_count"] = counts.get(session["id"], 0)
    return {"ok": True, **result}


@app.get("/api/dashboard/sessions/{session_id}/image/{variant}")
def dashboard_session_image(session_id: str, variant: str) -> FileResponse:
    image = dashboard_store.get_image(session_id, variant)
    if image is None:
        raise HTTPException(status_code=404, detail="Session image not found.")
    image_path, mime_type = image
    return FileResponse(
        image_path,
        media_type=mime_type,
        headers={"Cache-Control": "private, max-age=300"},
    )


@app.post("/api/generate")
async def generate(
    people_count: int = Form(...),
    scenario_id: str = Form(...),
    image: UploadFile | None = File(default=None),
) -> JSONResponse:
    """Validate one client-checked portrait and send exactly one provider request."""

    request_id = str(uuid.uuid4())
    logger = RequestLogger()
    generation_started = time.perf_counter()
    dashboard_started = False
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
            message="A captured photo is required to continue.",
            status_code=400,
            retryable=False,
        )

    mime_type = (image.content_type or "").lower()
    if mime_type not in ALLOWED_MIME_TYPES:
        return _error_response(
            request_id=request_id,
            logger=logger,
            code="IMAGE_UNSUPPORTED_TYPE",
            message="The captured photo format is not supported.",
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
            message="The captured photo is empty. Please try again.",
            status_code=400,
            retryable=False,
        )
    if len(image_bytes) > settings.max_upload_bytes:
        return _error_response(
            request_id=request_id,
            logger=logger,
            code="IMAGE_TOO_LARGE",
            message="The captured photo is larger than 10 MB. Please try again.",
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
            "response_modalities": ["IMAGE"],
        },
    )

    try:
        dashboard_store.start_session(
            session_id=request_id,
            people_count=people_count,
            scenario_id=normalized_scenario_id,
            image_bytes=image_bytes,
            mime_type=mime_type,
            logs=logger.entries(),
        )
        dashboard_started = True
    except Exception:
        # Dashboard persistence must never block a user's portrait generation.
        logger.add(
            "warning",
            "dashboard_recording_unavailable",
            "The dashboard could not record this generation attempt.",
        )

    try:
        result = await image_service.generate_image(
            image_bytes=image_bytes,
            mime_type=mime_type,
            prompt=generation_prompt,
            request_id=request_id,
        )
    except ProviderError as exc:
        response = _error_response(
            request_id=request_id,
            logger=logger,
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            retryable=exc.retryable,
            level="error",
            details={"http_status": exc.http_status, "latency_ms": exc.latency_ms},
        )
        if dashboard_started:
            try:
                dashboard_store.complete_failure(
                    session_id=request_id,
                    error_code=exc.code,
                    error_message=exc.message,
                    render_duration_ms=round((time.perf_counter() - generation_started) * 1000),
                    logs=logger.entries(),
                )
            except Exception:
                pass
        return response
    except Exception:
        response = _error_response(
            request_id=request_id,
            logger=logger,
            code="GENERATION_FAILED",
            message="The image service had a temporary problem.",
            status_code=502,
            retryable=True,
            level="error",
        )
        if dashboard_started:
            try:
                dashboard_store.complete_failure(
                    session_id=request_id,
                    error_code="GENERATION_FAILED",
                    error_message="The image service had a temporary problem.",
                    render_duration_ms=round((time.perf_counter() - generation_started) * 1000),
                    logs=logger.entries(),
                )
            except Exception:
                pass
        return response

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
    if dashboard_started:
        try:
            dashboard_store.complete_success(
                session_id=request_id,
                image_bytes=result.image_bytes,
                mime_type=result.mime_type,
                render_duration_ms=round((time.perf_counter() - generation_started) * 1000),
                logs=logger.entries(),
            )
        except Exception:
            pass
    result_image = f"data:{result.mime_type};base64,{base64.b64encode(result.image_bytes).decode('ascii')}"
    ticket = ""
    try:
        ticket = photo_service.issue_ticket(request_id, normalized_scenario_id)
    except Exception:
        logging.getLogger(__name__).exception("QR publish credential unavailable")
    payload = GenerationSuccessResponse(request_id=request_id, result_image=result_image,
                                        photo_publish_ticket=ticket, logs=logger.entries())
    return JSONResponse(status_code=200, content=payload.model_dump(mode="json"))


if FRONTEND_DIST.is_dir():
    @app.get("/{full_path:path}", include_in_schema=False)
    def frontend_spa(full_path: str) -> FileResponse:
        """Serve built assets and let the client-side dashboard route load directly."""

        if full_path == "api" or full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found.")

        frontend_root = FRONTEND_DIST.resolve()
        requested_path = (frontend_root / full_path).resolve()
        try:
            requested_path.relative_to(frontend_root)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail="File not found.") from exc

        if not requested_path.is_file():
            requested_path = frontend_root / "index.html"
        return FileResponse(requested_path)
