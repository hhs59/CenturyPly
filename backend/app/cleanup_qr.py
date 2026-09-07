"""Run expired QR file cleanup from a scheduler using the normal environment config."""
from .config import get_settings
from .photo_api import PhotoService


if __name__ == "__main__":
    PhotoService(get_settings()).cleanup()
    print("Expired QR photo cleanup complete.")
