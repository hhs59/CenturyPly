"""Provider-independent publishing and phone downloads of the final photo jacket."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
from io import BytesIO
import re
import secrets
import threading
import time
from urllib.parse import urlsplit

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse, Response
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, Field

from .photo_store import create_photo_store
from .services.image_generation import detect_raster_mime

TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]{32}$")
logger = logging.getLogger(__name__)


class DownloadRequest(BaseModel):
    event_id: str = Field(pattern=r"^[a-zA-Z0-9_-]{16,80}$")


class PhotoService:
    def __init__(self, settings):
        self.settings = settings
        self._store = None
        self._secret = None
        self._lock = threading.RLock()

    @property
    def store(self):
        with self._lock:
            if self._store is None:
                self._store = create_photo_store(self.settings)
            return self._store

    def secret(self):
        with self._lock:
            if self._secret is not None:
                return self._secret
            configured = self.settings.photo_signing_secret
            if configured:
                if len(configured) < 32:
                    raise ValueError("PHOTO_SIGNING_SECRET must contain at least 32 characters.")
                self._secret = configured.encode()
            elif self.settings.photo_storage_provider == "firebase":
                raise ValueError("Set PHOTO_SIGNING_SECRET for Firebase so all backend instances use the same key.")
            else:
                path = self.settings.dashboard_data_dir / "qr-signing.key"
                path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    with path.open("xb") as file:
                        file.write(secrets.token_bytes(32))
                    path.chmod(0o600)
                except FileExistsError:
                    pass
                self._secret = path.read_bytes()
            return self._secret

    def issue_ticket(self, request_id, scenario_id):
        data = {"request_id": request_id, "scenario_id": scenario_id,
                "token": secrets.token_urlsafe(24), "valid_until": int(time.time()) + 86400}
        payload = base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip("=")
        signature = hmac.new(self.secret(), payload.encode(), hashlib.sha256).hexdigest()
        return f"{payload}.{signature}"

    def verify_ticket(self, ticket):
        try:
            if len(ticket) > 2048:
                raise ValueError()
            payload, signature = ticket.split(".")
            expected = hmac.new(self.secret(), payload.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected):
                raise ValueError()
            data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
            if data["valid_until"] <= time.time() or not TOKEN_PATTERN.fullmatch(data["token"]):
                raise ValueError()
            return data
        except (ValueError, KeyError, TypeError) as exc:
            raise HTTPException(403, "This photo can no longer be published.") from exc

    def available(self, token):
        if not TOKEN_PATTERN.fullmatch(token):
            raise HTTPException(404, "Photo not found.")
        metadata = self.store.get(token)
        if not metadata:
            raise HTTPException(404, "Photo not found.")
        return metadata

    def public_metadata(self, token, metadata):
        origin = self.settings.public_app_url.rstrip("/")
        if origin:
            parsed = urlsplit(origin)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.path or parsed.query or parsed.fragment:
                raise ValueError("PUBLIC_APP_URL must be an HTTP(S) origin without a path.")
        return {"photo_url": f"{origin}/photo/{token}", "token": token,
                "image_url": f"/api/photos/{token}/image", "scenario_id": metadata["scenario_id"]}


def create_photo_router(service):
    router = APIRouter(prefix="/api/photos")

    @router.post("/publish")
    def publish(ticket: str = Form(...), image: UploadFile = File(...)):
        try:
            credential = service.verify_ticket(ticket)
            token = credential["token"]
            # Check origin configuration before saving anything.
            service.public_metadata(token, credential)
            existing = service.store.get(token)
            if existing:
                service.available(token)
                return service.public_metadata(token, existing)
            content = image.file.read(service.settings.max_final_photo_bytes + 1)
            if len(content) > service.settings.max_final_photo_bytes:
                raise HTTPException(413, "The final photo is too large.")
            if not content or detect_raster_mime(content) != "image/jpeg":
                raise HTTPException(400, "A final JPEG photo is required.")
            try:
                with Image.open(BytesIO(content)) as final_image:
                    if final_image.format != "JPEG" or final_image.size != (2160, 4301):
                        raise HTTPException(400, "The final photo must be a 2160×4301 JPEG.")
                    final_image.load()
            except (UnidentifiedImageError, OSError):
                raise HTTPException(400, "The final JPEG photo is corrupt.") from None
            now = int(time.time())
            metadata = {"request_id": credential["request_id"], "scenario_id": credential["scenario_id"],
                        "created_at": now}
            saved = service.store.publish(token, metadata, content)
            return service.public_metadata(token, saved)
        except HTTPException:
            raise
        except Exception:
            logger.exception("QR publishing failed")
            raise HTTPException(503, "Could not prepare your QR code. Please retry.") from None
        finally:
            image.file.close()

    @router.get("/{token}")
    def metadata(token: str):
        try:
            return JSONResponse(service.public_metadata(token, service.available(token)),
                                headers={"Cache-Control": "private, no-store", "Referrer-Policy": "no-referrer"})
        except HTTPException:
            raise
        except Exception:
            logger.exception("QR lookup failed")
            raise HTTPException(503, "Photo temporarily unavailable. Please retry.") from None

    def image_response(token, event=None):
        try:
            service.available(token)
            content = service.store.read(token)
            if event:
                service.store.record_download(token, event)
            headers = {"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"}
            if event:
                headers["Content-Disposition"] = 'attachment; filename="century-ply-portrait.jpg"'
            return Response(content, media_type="image/jpeg", headers=headers)
        except HTTPException:
            raise
        except FileNotFoundError:
            raise HTTPException(404, "Photo not found.") from None
        except Exception:
            logger.exception("QR image download failed")
            raise HTTPException(503, "Photo temporarily unavailable. Please retry.") from None

    @router.get("/{token}/image")
    def image(token: str):
        return image_response(token)

    # POST prevents link previews, QR scanners and browser prefetches counting as downloads.
    @router.post("/{token}/download")
    def download(token: str, body: DownloadRequest):
        return image_response(token, body.event_id)

    return router
