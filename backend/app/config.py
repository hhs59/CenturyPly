from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    gemini_api_key: str = ""
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1"
    image_model: str = "gemini-3.1-flash-image"
    image_timeout_seconds: float = 120.0
    max_upload_bytes: int = 10_485_760
    max_final_photo_bytes: int = 31_457_280
    frontend_origin: str = "http://localhost:5173"
    dashboard_data_dir: Path = PROJECT_ROOT / "backend" / "data"
    dashboard_timezone: str = "Asia/Ho_Chi_Minh"
    photo_storage_provider: Literal["local", "firebase"] = "local"
    public_app_url: str = ""
    photo_retention_days: int = Field(default=0, ge=0)
    photo_signing_secret: str = ""
    firebase_project_id: str = ""
    firebase_storage_bucket: str = ""
    firebase_service_account_json: str = ""
    firebase_photo_collection: str = "photobooth_photos"

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
