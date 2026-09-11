"""Optional one-time copy of live local QR photos to Firebase; dry-run by default."""
import argparse
import json
import re
import sqlite3
from pathlib import Path

from .config import get_settings
from .photo_store import FirebasePhotoStore


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-data-dir", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="Copy to the configured Firebase project; otherwise only inspect source.")
    args = parser.parse_args()
    directory = args.source_data_dir.resolve() / "qr"
    with sqlite3.connect((directory / "photos.sqlite3").as_uri() + "?mode=ro", uri=True) as database:
        rows = database.execute("SELECT token, metadata, downloads FROM photos").fetchall()
    eligible = []
    for token, raw, count in rows:
        source_metadata = json.loads(raw)
        metadata = {
            "request_id": source_metadata["request_id"],
            "scenario_id": source_metadata["scenario_id"],
            "created_at": source_metadata["created_at"],
        }
        if not re.fullmatch(r"[A-Za-z0-9_-]{32}", token):
            raise ValueError("Invalid source token; no files copied.")
        image = directory / f"{token}.jpg"
        if not image.is_file():
            raise FileNotFoundError(f"Missing source image for {token}; no files copied.")
        eligible.append((token, {**metadata, "download_count": count}, image))
    print(f"{len(eligible)} QR photos available to copy.")
    if not args.apply:
        print("Dry run only. Add --apply to copy into the configured Firebase project.")
        return
    target = FirebasePhotoStore(get_settings())
    for token, metadata, image in eligible:
        target.publish(token, metadata, image.read_bytes())
    print("Copy complete. Source files were retained; existing destination tokens were not overwritten.")


if __name__ == "__main__":
    main()
