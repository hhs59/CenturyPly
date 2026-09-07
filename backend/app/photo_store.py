"""QR persistence. Both providers implement the same small storage contract."""
from __future__ import annotations

import json
import hashlib
import sqlite3
import threading
import time
from pathlib import Path


class LocalPhotoStore:
    def __init__(self, directory: Path):
        self.directory = Path(directory) / "qr"
        self.directory.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.db = sqlite3.connect(self.directory / "photos.sqlite3", check_same_thread=False)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.execute("CREATE TABLE IF NOT EXISTS photos (token TEXT PRIMARY KEY, metadata TEXT NOT NULL, downloads INTEGER NOT NULL DEFAULT 0)")
        self.db.execute("CREATE TABLE IF NOT EXISTS downloads (token TEXT, event TEXT, PRIMARY KEY(token, event))")
        self.db.commit()

    def get(self, token):
        with self.lock:
            row = self.db.execute("SELECT metadata FROM photos WHERE token=?", (token,)).fetchone()
        return json.loads(row[0]) if row else None

    def publish(self, token, metadata, image):
        with self.lock:
            existing = self.get(token)
            if existing:
                return existing
            path = self.directory / f"{token}.jpg"
            temporary = path.with_suffix(".tmp")
            temporary.write_bytes(image)
            temporary.replace(path)
            with self.db:
                self.db.execute("INSERT INTO photos(token,metadata) VALUES (?,?)", (token, json.dumps(metadata)))
        return metadata

    def read(self, token):
        return (self.directory / f"{token}.jpg").read_bytes()

    def record_download(self, token, event):
        with self.lock, self.db:
            added = self.db.execute("INSERT OR IGNORE INTO downloads VALUES (?,?)", (token, event)).rowcount
            if added:
                self.db.execute("UPDATE photos SET downloads=downloads+1 WHERE token=?", (token,))

    def counts(self):
        with self.lock:
            rows = self.db.execute("SELECT metadata, downloads FROM photos").fetchall()
        return {json.loads(row[0])["request_id"]: row[1] for row in rows}

    def cleanup(self):
        with self.lock:
            rows = self.db.execute("SELECT token, metadata FROM photos").fetchall()
            for token, raw in rows:
                metadata = json.loads(raw)
                if metadata.get("expires_at") and metadata["expires_at"] <= time.time():
                    (self.directory / f"{token}.jpg").unlink(missing_ok=True)
                    # Retain the count and expiry tombstone, discard click deduplication data.
                    with self.db:
                        self.db.execute("DELETE FROM downloads WHERE token=?", (token,))


class FirebasePhotoStore:
    def __init__(self, settings):
        import firebase_admin
        from firebase_admin import credentials, firestore, storage

        if not settings.firebase_project_id or not settings.firebase_storage_bucket:
            raise ValueError("Firebase QR storage requires FIREBASE_PROJECT_ID and FIREBASE_STORAGE_BUCKET.")
        name = "qr-" + hashlib.sha256(f"{settings.firebase_project_id}:{settings.firebase_storage_bucket}".encode()).hexdigest()[:16]
        try:
            app = firebase_admin.get_app(name)
        except ValueError:
            credential = (credentials.Certificate(json.loads(settings.firebase_service_account_json))
                          if settings.firebase_service_account_json else credentials.ApplicationDefault())
            app = firebase_admin.initialize_app(credential, {
                "projectId": settings.firebase_project_id,
                "storageBucket": settings.firebase_storage_bucket,
            }, name=name)
        self.db = firestore.client(app)
        self.collection = self.db.collection(settings.firebase_photo_collection)
        self.bucket = storage.bucket(app=app)
        self.firestore = firestore

    def get(self, token):
        return self.collection.document(token).get(timeout=15).to_dict()

    def blob(self, token):
        return self.bucket.blob(f"{self.collection.id}/{token}/final.jpg")

    def publish(self, token, metadata, image):
        from google.api_core.exceptions import AlreadyExists, PreconditionFailed

        existing = self.get(token)
        if existing:
            return existing
        blob = self.blob(token)
        try:
            blob.upload_from_string(image, content_type="image/jpeg", if_generation_match=0, timeout=30)
        except PreconditionFailed:
            # An earlier attempt may have uploaded the file before its metadata write failed.
            pass
        try:
            self.collection.document(token).create({"download_count": 0, **metadata}, timeout=15)
        except AlreadyExists:
            pass
        return self.get(token)

    def read(self, token):
        from google.api_core.exceptions import NotFound
        try:
            return self.blob(token).download_as_bytes(timeout=30)
        except NotFound as exc:
            raise FileNotFoundError(token) from exc

    def record_download(self, token, event):
        photo = self.collection.document(token)
        receipt = photo.collection("downloads").document(event)

        @self.firestore.transactional
        def record(transaction):
            if not receipt.get(transaction=transaction).exists:
                transaction.create(receipt, {"created_at": self.firestore.SERVER_TIMESTAMP})
                transaction.update(photo, {"download_count": self.firestore.Increment(1)})

        record(self.db.transaction())

    def counts(self):
        return {row.get("request_id"): row.get("download_count")
                for row in self.collection.select(["request_id", "download_count"]).stream(timeout=15)}

    def cleanup(self):
        from google.api_core.exceptions import NotFound
        from google.cloud.firestore_v1.base_query import FieldFilter

        query = self.collection.where(filter=FieldFilter("expires_at", "<=", time.time()))
        for snapshot in query.stream(timeout=30):
            metadata = snapshot.to_dict()
            if not metadata.get("expires_at") or metadata.get("purged"):
                continue
            try:
                self.blob(snapshot.id).delete(timeout=15)
            except NotFound:
                pass
            for event in snapshot.reference.collection("downloads").stream(timeout=15):
                event.reference.delete(timeout=15)
            snapshot.reference.update({"purged": True}, timeout=15)


def create_photo_store(settings):
    if settings.photo_storage_provider == "firebase":
        return FirebasePhotoStore(settings)
    return LocalPhotoStore(settings.dashboard_data_dir)
