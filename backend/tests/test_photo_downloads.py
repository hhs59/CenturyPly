"""Run with: python -m unittest discover -s backend/tests -v (from repo root).

Firebase tests use SDK doubles: no cloud writes or billable Gemini calls.
"""
import tempfile
import importlib
from io import BytesIO
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from firebase_admin import firestore
from PIL import Image
from google.api_core.exceptions import AlreadyExists, NotFound, PreconditionFailed

from backend.app.config import Settings
from backend.app.photo_api import PhotoService, create_photo_router
from backend.app.photo_store import FirebasePhotoStore

def jpeg_fixture(size=(4320, 7680)):
    output = BytesIO()
    with Image.new("RGB", size, "white") as image:
        image.save(output, "JPEG", quality=1)
    return output.getvalue()


JPEG = jpeg_fixture()
WRONG_SIZE_JPEG = jpeg_fixture((768, 1365))
FORGED_JPEG = b"\xff\xd8\xff\xc0\x00\x11\x08\x1e\x00\x10\xe0\x03\x01\x11\x00\x02\x11\x00\x03\x11\x00\xff\xd9"


def firebase_double():
    """Exercise the Firebase adapter with in-memory SDK boundaries."""
    docs, images = {}, {}
    lock = threading.RLock()
    db = MagicMock()

    def reference(path):
        ref = MagicMock()
        ref.path = path
        ref.id = path.split("/")[-1]
        def snapshot(**_):
            snap = MagicMock()
            snap.exists = path in docs
            snap.reference = ref
            snap.id = ref.id
            snap.to_dict.side_effect = lambda: dict(docs[path]) if path in docs else None
            snap.get.side_effect = lambda key: docs[path][key]
            return snap
        def create(data, **_):
            if path in docs:
                raise AlreadyExists("exists")
            docs[path] = dict(data)
        def update(data, **_):
            for key, value in data.items():
                docs[path][key] = docs[path].get(key, 0) + value.value if isinstance(value, firestore.Increment) else value
        ref.get.side_effect = snapshot
        ref.create.side_effect = create
        ref.update.side_effect = update
        ref.delete.side_effect = lambda **_: docs.pop(path, None)
        ref.collection.side_effect = lambda name: collection(f"{path}/{name}")
        return ref

    def collection(path):
        col = MagicMock()
        col.id = path.split("/")[-1]
        col.document.side_effect = lambda name: reference(f"{path}/{name}")
        col.select.return_value = col
        col.where.return_value = col
        col.stream.side_effect = lambda **_: iter([reference(key).get() for key in list(docs)
                                                 if key.startswith(path + "/") and key.count("/") == path.count("/") + 1])
        return col

    def blob(path):
        obj = MagicMock()
        def upload(data, **options):
            if options.get("if_generation_match") == 0 and path in images:
                raise PreconditionFailed("exists")
            images[path] = data
        def read(**_):
            if path not in images:
                raise NotFound("missing")
            return images[path]
        obj.upload_from_string.side_effect = upload
        obj.download_as_bytes.side_effect = read
        obj.delete.side_effect = lambda **_: images.pop(path, None)
        return obj

    transaction = MagicMock()
    transaction.create.side_effect = lambda ref, data: ref.create(data)
    transaction.update.side_effect = lambda ref, data: ref.update(data)
    db.transaction.return_value = transaction
    db.collection.side_effect = collection
    bucket = MagicMock()
    bucket.blob.side_effect = blob
    def transactional(function):
        def wrapped(tx):
            with lock:
                return function(tx)
        return wrapped
    store = FirebasePhotoStore.__new__(FirebasePhotoStore)
    store.db = db
    store.collection = collection("photobooth_photos")
    store.bucket = bucket
    store.firestore = SimpleNamespace(transactional=transactional, Increment=firestore.Increment, SERVER_TIMESTAMP=firestore.SERVER_TIMESTAMP)
    return store


class PhotoContract:
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.settings = Settings(_env_file=None, dashboard_data_dir=Path(self.temporary.name),
                                 photo_signing_secret="test-secret-" * 4, public_app_url="https://photos.example.com")
        self.service = PhotoService(self.settings)
        self.addCleanup(lambda: self.service._store.db.close() if self.service._store else None)
        if self.firebase:
            self.service._store = firebase_double()
        self.app = FastAPI()
        self.app.include_router(create_photo_router(self.service))
        self.client = TestClient(self.app)
        self.addCleanup(self.client.close)
        self.ticket = self.service.issue_ticket("test-generation", "thang-long-imperial")

    def publish(self, ticket=None, content=JPEG):
        return self.client.post("/api/photos/publish", data={"ticket": ticket or self.ticket},
                                files={"image": ("final.jpg", content, "image/jpeg")})

    def test_publish_retry_preserves_link_and_exact_branded_bytes(self):
        first = self.publish()
        self.assertEqual(first.status_code, 200, first.text)
        token = first.json()["token"]
        self.assertEqual(first.json()["photo_url"], f"https://photos.example.com/photo/{token}")
        self.assertEqual(self.publish(content=JPEG + b"another image").json(), first.json())
        self.assertEqual(self.client.get(first.json()["image_url"]).content, JPEG)

    def test_preview_and_get_requests_never_count_downloads(self):
        token = self.publish().json()["token"]
        self.assertEqual(self.client.get(f"/api/photos/{token}").status_code, 200)
        self.assertEqual(self.client.get(f"/api/photos/{token}/image").status_code, 200)
        self.assertEqual(self.client.get(f"/api/photos/{token}/download").status_code, 405)
        self.assertEqual(self.service.store.counts()["test-generation"], 0)

    def test_download_retry_counts_once_and_distinct_presses_count_again(self):
        token = self.publish().json()["token"]
        url = f"/api/photos/{token}/download"
        for _ in range(2):
            response = self.client.post(url, json={"event_id": "download-press-00001"})
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.content, JPEG)
            self.assertIn("attachment", response.headers["content-disposition"])
        self.assertEqual(self.service.store.counts()["test-generation"], 1)
        self.client.post(url, json={"event_id": "download-press-00002"})
        self.assertEqual(self.service.store.counts()["test-generation"], 2)

    def test_concurrent_counter_updates(self):
        token = self.publish().json()["token"]
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda _: self.service.store.record_download(token, "same-download-event"), range(12)))
        self.assertEqual(self.service.store.counts()["test-generation"], 1)

    def test_unsigned_invalid_and_expired_publish_credentials_rejected(self):
        self.assertEqual(self.publish(ticket="invalid").status_code, 403)
        self.assertEqual(self.publish(ticket=self.ticket[:-1] + ("a" if self.ticket[-1] != "a" else "b")).status_code, 403)
        with patch("backend.app.photo_api.time.time", return_value=time.time() + 86401):
            self.assertEqual(self.publish().status_code, 403)

    def test_expiry_blocks_preview_download_and_republish_then_removes_image(self):
        self.settings.photo_retention_days = 1
        token = self.publish().json()["token"]
        with patch("time.time", return_value=time.time() + 86401):
            for path in (f"/api/photos/{token}", f"/api/photos/{token}/image"):
                self.assertEqual(self.client.get(path).status_code, 410)
            self.assertEqual(self.client.post(f"/api/photos/{token}/download", json={"event_id": "download-press-00001"}).status_code, 410)
            self.service.cleanup()
        with self.assertRaises(FileNotFoundError):
            self.service.store.read(token)
        self.assertEqual(self.service.store.counts()["test-generation"], 0)

    def test_invalid_images_unknown_tokens_and_upload_limits(self):
        self.assertEqual(self.publish(content=b"not an image").status_code, 400)
        self.assertEqual(self.publish(content=FORGED_JPEG).status_code, 400)
        self.assertEqual(self.publish(content=JPEG[:-2]).status_code, 400)
        self.assertEqual(self.publish(content=WRONG_SIZE_JPEG).status_code, 400)
        self.settings.max_final_photo_bytes = 10
        self.assertEqual(self.publish().status_code, 413)
        self.assertEqual(self.client.get("/api/photos/" + "x" * 32).status_code, 404)
        self.assertEqual(self.client.get("/api/photos/bad-token").status_code, 404)

    def test_storage_failure_allows_retry_with_same_ticket(self):
        store = self.service.store
        with patch.object(store, "publish", side_effect=OSError("offline")):
            with self.assertLogs("backend.app.photo_api", level="ERROR"):
                self.assertEqual(self.publish().status_code, 503)
        self.assertEqual(self.publish().status_code, 200)

    def test_zero_retention_keeps_photos(self):
        token = self.publish().json()["token"]
        with patch("time.time", return_value=time.time() + 86400 * 365):
            self.service.cleanup()
            self.assertEqual(self.client.get(f"/api/photos/{token}/image").content, JPEG)


class LocalPhotoTests(PhotoContract, unittest.TestCase):
    firebase = False

    def test_restart_preserves_photo_key_and_count(self):
        token = self.publish().json()["token"]
        self.service.store.record_download(token, "download-press-00001")
        restarted = PhotoService(self.settings)
        self.addCleanup(lambda: restarted.store.db.close())
        self.assertEqual(restarted.store.read(token), JPEG)
        self.assertEqual(restarted.store.counts()["test-generation"], 1)
        self.assertEqual(restarted.verify_ticket(self.ticket)["token"], token)


class FirebasePhotoTests(PhotoContract, unittest.TestCase):
    firebase = True

    def test_configuration_selects_firebase_without_changing_router(self):
        settings = self.settings.model_copy(update={"photo_storage_provider": "firebase"})
        with patch("backend.app.photo_store.FirebasePhotoStore", return_value=self.service.store) as provider:
            switched = PhotoService(settings)
            app = FastAPI()
            app.include_router(create_photo_router(switched))
            with TestClient(app) as client:
                response = client.post("/api/photos/publish", data={"ticket": self.ticket},
                                       files={"image": ("final.jpg", JPEG, "image/jpeg")})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(client.get(response.json()["image_url"]).content, JPEG)
            provider.assert_called_once_with(settings)

    def test_import_preserves_download_counts_and_never_overwrites_them(self):
        token = self.service.verify_ticket(self.ticket)["token"]
        metadata = {"request_id": "migrated-request", "scenario_id": "thang-long-imperial",
                    "created_at": int(time.time()), "expires_at": None, "download_count": 5}
        self.service.store.publish(token, metadata, JPEG)
        self.service.store.record_download(token, "download-after-migration")
        self.service.store.publish(token, metadata, JPEG)
        self.assertEqual(self.service.store.counts()["migrated-request"], 6)

    def test_retry_after_metadata_failure_uses_existing_storage_object(self):
        store = self.service.store
        # Inject a failure in the first metadata create after a successful object upload.
        original = store.collection.document.side_effect
        def failing_reference(token):
            ref = original(token)
            ref.create.side_effect = OSError("temporary Firestore outage")
            return ref
        store.collection.document.side_effect = failing_reference
        try:
            with self.assertLogs("backend.app.photo_api", level="ERROR"):
                self.assertEqual(self.publish().status_code, 503)
        finally:
            store.collection.document.side_effect = original
        self.assertEqual(self.publish().status_code, 200)


class GenerationQrIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(temporary.cleanup)
        settings = Settings(_env_file=None, dashboard_data_dir=Path(temporary.name),
                            photo_signing_secret="test-integration-secret-" * 3)
        with patch("backend.app.config.get_settings", return_value=settings):
            cls.main = importlib.import_module("backend.app.main")
        cls.addClassCleanup(cls.main.dashboard_store.close)
        cls.addClassCleanup(lambda: cls.main.photo_service.store.db.close())

    def test_generation_publish_phone_download_and_dashboard(self):
        from backend.app.services.image_generation import ProviderImageResult
        result = ProviderImageResult(JPEG, "image/jpeg", 4320, 7680, 1, 200)
        with TestClient(self.main.app) as client, patch.object(self.main.image_service, "generate_image", new=AsyncMock(return_value=result)):
            generated = client.post("/api/generate", data={"people_count": 4, "scenario_id": next(iter(self.main.SCENARIO_IDS))},
                                    files={"image": ("input.jpg", JPEG, "image/jpeg")})
            self.assertEqual(generated.status_code, 200, generated.text)
            payload = generated.json()
            self.assertTrue(payload["photo_publish_ticket"])
            published = client.post("/api/photos/publish", data={"ticket": payload["photo_publish_ticket"]},
                                    files={"image": ("final.jpg", JPEG, "image/jpeg")})
            self.assertEqual(published.status_code, 200, published.text)
            token = published.json()["token"]
            self.assertEqual(client.post(f"/api/photos/{token}/download", json={"event_id": "integration-download-0001"}).content, JPEG)
            sessions = client.get("/api/dashboard/sessions").json()["data"]
            session = next(row for row in sessions if row["id"] == payload["request_id"])
            self.assertEqual(session["download_count"], 1)
            self.assertEqual(client.get("/api/dashboard/overview").json()["total_downloads"], 1)
            self.assertEqual(client.post(f"/api/dashboard/sessions/{payload['request_id']}/action", json={"action": "download"}).status_code, 405)

    def test_qr_configuration_failure_does_not_lose_generated_portrait(self):
        from backend.app.services.image_generation import ProviderImageResult
        result = ProviderImageResult(JPEG, "image/jpeg", 4320, 7680, 1, 200)
        with TestClient(self.main.app) as client, patch.object(self.main.image_service, "generate_image", new=AsyncMock(return_value=result)), patch.object(self.main.photo_service, "issue_ticket", side_effect=ValueError("missing config")):
            with self.assertLogs("backend.app.main", level="ERROR"):
                response = client.post("/api/generate", data={"people_count": 1, "scenario_id": next(iter(self.main.SCENARIO_IDS))},
                                       files={"image": ("input.jpg", JPEG, "image/jpeg")})
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json()["result_image"].startswith("data:image/jpeg;base64,"))
            self.assertEqual(response.json()["photo_publish_ticket"], "")


if __name__ == "__main__":
    unittest.main()
