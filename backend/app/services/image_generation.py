from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
import time
from typing import Any

import httpx

from ..config import Settings


ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}


@dataclass(frozen=True)
class ProviderImageResult:
    image_bytes: bytes
    mime_type: str
    latency_ms: int
    http_status: int


class ProviderError(RuntimeError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int = 502,
        retryable: bool = True,
        http_status: int | None = None,
        latency_ms: int = 0,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.retryable = retryable
        self.http_status = http_status
        self.latency_ms = latency_ms


class ImageGenerationService:
    def __init__(self, settings: Settings):
        self.settings = settings

    # Send one portrait to OpenRouter and return its first generated image.
    async def generate_image(
        self,
        *,
        image_bytes: bytes,
        mime_type: str,
        prompt: str,
        request_id: str,
    ) -> ProviderImageResult:
        api_key = self.settings.openrouter_api_key.strip()
        if not api_key:
            raise ProviderError(
                "PROVIDER_NOT_CONFIGURED",
                "The image service is not configured.",
                status_code=503,
                retryable=False,
            )

        image_data_url = f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('ascii')}"
        payload = {
            "model": self.settings.image_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_data_url}},
                    ],
                }
            ],
            "modalities": ["image", "text"],
            "image_config": {"aspect_ratio": "3:4"},
            "max_tokens": 4096,
        }
        endpoint = f"{self.settings.openrouter_base_url.rstrip('/')}/chat/completions"
        started = time.perf_counter()

        try:
            async with httpx.AsyncClient(timeout=self.settings.image_timeout_seconds) as client:
                response = await client.post(
                    endpoint,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "X-Request-ID": request_id,
                    },
                    json=payload,
                )
        except httpx.TimeoutException as exc:
            raise ProviderError(
                "PROVIDER_TIMEOUT",
                "Generation took too long. Please try again.",
                status_code=504,
                latency_ms=_latency_ms(started),
            ) from exc
        except httpx.RequestError as exc:
            raise ProviderError(
                "PROVIDER_UNAVAILABLE",
                "The image service had a temporary problem.",
                latency_ms=_latency_ms(started),
            ) from exc

        latency_ms = _latency_ms(started)
        if not response.is_success:
            raise _http_error(response.status_code, latency_ms)

        try:
            response_body = response.json()
        except (ValueError, UnicodeDecodeError) as exc:
            raise ProviderError(
                "PROVIDER_INVALID_RESPONSE",
                "The image service returned an invalid response.",
                http_status=response.status_code,
                latency_ms=latency_ms,
            ) from exc

        image_bytes, returned_mime_type = decode_provider_image(response_body)
        return ProviderImageResult(
            image_bytes=image_bytes,
            mime_type=returned_mime_type,
            latency_ms=latency_ms,
            http_status=response.status_code,
        )


def _latency_ms(started: float) -> int:
    return round((time.perf_counter() - started) * 1000)


def _http_error(http_status: int, latency_ms: int) -> ProviderError:
    if http_status in (401, 403):
        return ProviderError(
            "PROVIDER_AUTH_ERROR",
            "The image service is temporarily unavailable.",
            status_code=503,
            retryable=False,
            http_status=http_status,
            latency_ms=latency_ms,
        )
    if http_status == 402:
        return ProviderError(
            "PROVIDER_BILLING_ERROR",
            "The image service is temporarily unavailable.",
            status_code=503,
            retryable=False,
            http_status=http_status,
            latency_ms=latency_ms,
        )
    if http_status == 429:
        return ProviderError(
            "PROVIDER_RATE_LIMIT",
            "The image service is busy. Try again shortly.",
            status_code=429,
            http_status=http_status,
            latency_ms=latency_ms,
        )
    return ProviderError(
        "PROVIDER_UNAVAILABLE",
        "The image service had a temporary problem.",
        http_status=http_status,
        latency_ms=latency_ms,
    )


# OpenRouter returns the image as a Base64 data URL in the assistant message.
def decode_provider_image(response_body: Any) -> tuple[bytes, str]:
    try:
        data_url = response_body["choices"][0]["message"]["images"][0]["image_url"]["url"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderError("PROVIDER_NO_IMAGE", "No image was returned. Please try again.") from exc

    if not isinstance(data_url, str) or not data_url:
        raise ProviderError("PROVIDER_NO_IMAGE", "No image was returned. Please try again.")

    if not data_url.startswith("data:"):
        raise ProviderError("PROVIDER_INVALID_IMAGE", "The returned image could not be processed.")

    header, separator, encoded = data_url.partition(",")
    if not separator or ";base64" not in header:
        raise ProviderError("PROVIDER_INVALID_IMAGE", "The returned image could not be processed.")
    declared_mime_type = header[5:].split(";", 1)[0]

    try:
        image_bytes = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ProviderError("PROVIDER_INVALID_IMAGE", "The returned image could not be processed.") from exc

    detected_mime_type = detect_raster_mime(image_bytes)
    if detected_mime_type is None:
        raise ProviderError("PROVIDER_INVALID_IMAGE", "The returned image could not be processed.")
    if declared_mime_type and declared_mime_type != detected_mime_type:
        raise ProviderError("PROVIDER_INVALID_IMAGE", "The returned image could not be processed.")
    return image_bytes, detected_mime_type


# Basic signatures are enough here; the image provider performs the real decode.
def detect_raster_mime(image_bytes: bytes) -> str | None:
    if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if image_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if len(image_bytes) >= 12 and image_bytes.startswith(b"RIFF") and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    return None
