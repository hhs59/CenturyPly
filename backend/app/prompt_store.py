"""Small JSON-backed store for the admin-editable generation prompts."""

from __future__ import annotations

import json
import mimetypes
import os
from pathlib import Path
from threading import RLock
from typing import Any

from .prompts import REFERENCE_ROOT, SCENARIO_CONFIGS, SCENARIO_IDS, default_prompt_configuration, split_scenario_prompt


PROMPT_FILE_NAME = "prompts.json"
REFERENCE_DIRECTORY_NAME = "prompt_references"
MAX_BASE_PROMPT_LENGTH = 40_000
MAX_SCENARIO_PROMPT_LENGTH = 12_000
REQUIRED_BASE_PLACEHOLDERS = ("{people_count}", "{variation_hint}", "{pose_expression}")
REFERENCE_ROLES = ("male_clothing", "female_clothing", "location")
REFERENCE_MIME_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
REFERENCE_LABELS = {
    "male_clothing": "ẢNH 2 — mẫu tham chiếu trang phục nam; chỉ lấy trang phục",
    "female_clothing": "ẢNH 3 — mẫu tham chiếu trang phục nữ; chỉ lấy trang phục",
    "location": "ẢNH 4 — mẫu tham chiếu địa điểm; chỉ lấy kiến trúc và không gian",
}


class PromptConfigurationError(ValueError):
    """Raised when the admin submits an unsafe or incomplete prompt config."""


def _text(value: Any, field_name: str, max_length: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PromptConfigurationError(f"{field_name} must be a non-empty text value.")
    if len(value) > max_length:
        raise PromptConfigurationError(f"{field_name} is too long.")
    return value


def _scenario_fields(item: dict[str, Any], scenario_id: str) -> dict[str, str]:
    """Normalize the new fields while migrating the previous combined shape."""

    if all(key in item for key in ("concept_prompt", "male_clothing", "female_clothing", "pose_expression")):
        return {
            "concept_prompt": _text(item.get("concept_prompt"), f"scenarios.{scenario_id}.concept_prompt", MAX_SCENARIO_PROMPT_LENGTH),
            "male_clothing": _text(item.get("male_clothing"), f"scenarios.{scenario_id}.male_clothing", MAX_SCENARIO_PROMPT_LENGTH),
            "female_clothing": _text(item.get("female_clothing"), f"scenarios.{scenario_id}.female_clothing", MAX_SCENARIO_PROMPT_LENGTH),
            "pose_expression": _text(item.get("pose_expression"), f"scenarios.{scenario_id}.pose_expression", MAX_SCENARIO_PROMPT_LENGTH),
        }

    if "prompt" in item and "pose_expression" in item:
        legacy_fields = split_scenario_prompt(_text(item.get("prompt"), f"scenarios.{scenario_id}.prompt", MAX_SCENARIO_PROMPT_LENGTH))
        return {
            **legacy_fields,
            "pose_expression": _text(item.get("pose_expression"), f"scenarios.{scenario_id}.pose_expression", MAX_SCENARIO_PROMPT_LENGTH),
        }

    raise PromptConfigurationError(f"Missing prompt fields for scenario: {scenario_id}.")


def validate_prompt_configuration(payload: Any) -> dict[str, Any]:
    """Validate and normalize a complete configuration submitted by the UI."""

    if not isinstance(payload, dict):
        raise PromptConfigurationError("Prompt configuration must be an object.")

    base_prompt = _text(payload.get("base_prompt"), "base_prompt", MAX_BASE_PROMPT_LENGTH)
    missing_placeholders = [placeholder for placeholder in REQUIRED_BASE_PLACEHOLDERS if placeholder not in base_prompt]
    if missing_placeholders:
        missing = ", ".join(missing_placeholders)
        raise PromptConfigurationError(f"base_prompt must keep these placeholders: {missing}.")

    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, dict):
        raise PromptConfigurationError("scenarios must be an object.")

    normalized_scenarios: dict[str, dict[str, str]] = {}
    for scenario_id in sorted(SCENARIO_IDS):
        item = scenarios.get(scenario_id)
        if not isinstance(item, dict):
            raise PromptConfigurationError(f"Missing prompt for scenario: {scenario_id}.")
        normalized_scenarios[scenario_id] = _scenario_fields(item, scenario_id)

    return {"base_prompt": base_prompt, "scenarios": normalized_scenarios}


class PromptStore:
    """Persist prompt edits under the configured data directory.

    The store falls back to the source defaults if the file is missing or was
    damaged, so a bad admin edit cannot stop image generation.
    """

    def __init__(self, data_dir: str | Path) -> None:
        self.data_dir = Path(data_dir).expanduser()
        self.path = self.data_dir / PROMPT_FILE_NAME
        self.reference_dir = self.data_dir / REFERENCE_DIRECTORY_NAME
        self._lock = RLock()

    @staticmethod
    def defaults() -> dict[str, Any]:
        return default_prompt_configuration()

    def read(self) -> dict[str, Any]:
        with self._lock:
            if not self.path.is_file():
                return self.defaults()
            try:
                payload = json.loads(self.path.read_text(encoding="utf-8"))
                return validate_prompt_configuration(payload)
            except (OSError, json.JSONDecodeError, PromptConfigurationError, TypeError):
                return self.defaults()

    def save(self, payload: Any) -> dict[str, Any]:
        normalized = validate_prompt_configuration(payload)
        encoded = json.dumps(normalized, ensure_ascii=False, indent=2) + "\n"
        with self._lock:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            temporary_path = self.path.with_suffix(".json.tmp")
            temporary_path.write_text(encoded, encoding="utf-8")
            os.replace(temporary_path, self.path)
        return normalized

    def reset(self) -> dict[str, Any]:
        with self._lock:
            if self.reference_dir.is_dir():
                for scenario_id in SCENARIO_IDS:
                    for role in REFERENCE_ROLES:
                        for candidate in self._reference_candidates(scenario_id, role):
                            candidate.unlink(missing_ok=True)
        return self.save(self.defaults())

    @staticmethod
    def validate_reference_key(scenario_id: str, role: str) -> None:
        if scenario_id not in SCENARIO_IDS:
            raise PromptConfigurationError("scenario_id is not supported.")
        if role not in REFERENCE_ROLES:
            raise PromptConfigurationError("reference role is not supported.")

    def _reference_candidates(self, scenario_id: str, role: str) -> list[Path]:
        return [self.reference_dir / scenario_id / f"{role}{extension}" for extension in REFERENCE_MIME_EXTENSIONS.values()]

    def reference_path(self, scenario_id: str, role: str) -> Path:
        self.validate_reference_key(scenario_id, role)
        for candidate in self._reference_candidates(scenario_id, role):
            if candidate.is_file():
                return candidate

        config = SCENARIO_CONFIGS[scenario_id]
        default_name = {
            "male_clothing": config["male"],
            "female_clothing": config["female"],
            "location": config["location"],
        }[role]
        default_directory = "locations" if role == "location" else "clothing"
        return REFERENCE_ROOT / default_directory / default_name

    def reference_urls(self) -> dict[str, dict[str, str]]:
        return {
            scenario_id: {
                role: f"/api/prompts/references/{scenario_id}/{role}"
                for role in REFERENCE_ROLES
            }
            for scenario_id in sorted(SCENARIO_IDS)
        }

    def reference_media_type(self, path: Path) -> str:
        if path.suffix.lower() == ".jpg":
            return "image/jpeg"
        return mimetypes.guess_type(path.name)[0] or "image/jpeg"

    def load_references(self, scenario_id: str) -> list[tuple[str, bytes, str]]:
        self.validate_reference_key(scenario_id, "location")
        references = []
        for role in REFERENCE_ROLES:
            path = self.reference_path(scenario_id, role)
            references.append((REFERENCE_LABELS[role], path.read_bytes(), self.reference_media_type(path)))
        return references

    def save_reference(self, scenario_id: str, role: str, image_bytes: bytes, mime_type: str) -> Path:
        self.validate_reference_key(scenario_id, role)
        extension = REFERENCE_MIME_EXTENSIONS.get(mime_type)
        if not extension:
            raise PromptConfigurationError("Reference image format is not supported.")

        with self._lock:
            directory = self.reference_dir / scenario_id
            directory.mkdir(parents=True, exist_ok=True)
            for candidate in self._reference_candidates(scenario_id, role):
                candidate.unlink(missing_ok=True)
            target = directory / f"{role}{extension}"
            temporary_path = directory / f".{role}.uploading"
            temporary_path.write_bytes(image_bytes)
            os.replace(temporary_path, target)
            return target

    def reset_reference(self, scenario_id: str, role: str) -> None:
        self.validate_reference_key(scenario_id, role)
        with self._lock:
            for candidate in self._reference_candidates(scenario_id, role):
                candidate.unlink(missing_ok=True)
