from __future__ import annotations

import json
import re
import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo


MIME_EXTENSIONS = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}
MAX_LOG_ENTRIES = 250
MAX_LOG_STRING_LENGTH = 4_000
SESSION_ID_PATTERN = re.compile(r"[^a-zA-Z0-9_-]")


class DashboardStore:
    """Durable, local session history for the photobooth dashboard.

    The original VIN dashboard reads Firestore. This app is intentionally
    self-contained, so SQLite plus a small media folder gives the dashboard
    the same useful history without introducing a second cloud dependency.
    """

    def __init__(self, data_dir: str | Path, timezone_name: str = "Asia/Ho_Chi_Minh") -> None:
        self.data_dir = Path(data_dir).expanduser()
        self.media_dir = self.data_dir / "sessions"
        self.db_path = self.data_dir / "dashboard.sqlite3"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.media_dir.mkdir(parents=True, exist_ok=True)
        try:
            self.display_timezone = ZoneInfo(timezone_name)
        except Exception:
            self.display_timezone = timezone.utc
        self._lock = threading.RLock()
        self._connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA busy_timeout=5000")
        self._initialize()

    def _initialize(self) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    people_count INTEGER NOT NULL,
                    scenario_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    render_duration_ms INTEGER NOT NULL DEFAULT 0,
                    input_mime_type TEXT,
                    input_byte_count INTEGER NOT NULL DEFAULT 0,
                    output_mime_type TEXT,
                    output_byte_count INTEGER NOT NULL DEFAULT 0,
                    error_code TEXT,
                    error_message TEXT,
                    logs_json TEXT NOT NULL DEFAULT '[]',
                    input_path TEXT,
                    output_path TEXT
                )
                """
            )
            self._connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at DESC)"
            )
            self._connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_sessions_scenario_id ON sessions(scenario_id)"
            )

    def close(self) -> None:
        with self._lock:
            self._connection.close()

    def start_session(
        self,
        *,
        session_id: str,
        people_count: int,
        scenario_id: str,
        image_bytes: bytes,
        mime_type: str,
        logs: Iterable[Any] = (),
    ) -> None:
        safe_id = _safe_session_id(session_id)
        extension = MIME_EXTENSIONS.get(mime_type, "bin")
        session_dir = self.media_dir / safe_id
        session_dir.mkdir(parents=True, exist_ok=True)
        input_path = session_dir / f"input.{extension}"
        input_path.write_bytes(image_bytes)
        created_at = _utc_now()
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO sessions (
                    id, people_count, scenario_id, status, created_at,
                    input_mime_type, input_byte_count, logs_json, input_path
                ) VALUES (?, ?, ?, 'running', ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    people_count = excluded.people_count,
                    scenario_id = excluded.scenario_id,
                    status = 'running',
                    created_at = excluded.created_at,
                    completed_at = NULL,
                    render_duration_ms = 0,
                    input_mime_type = excluded.input_mime_type,
                    input_byte_count = excluded.input_byte_count,
                    output_mime_type = NULL,
                    output_byte_count = 0,
                    error_code = NULL,
                    error_message = NULL,
                    logs_json = excluded.logs_json,
                    input_path = excluded.input_path,
                    output_path = NULL
                """,
                (
                    session_id,
                    people_count,
                    scenario_id,
                    created_at,
                    mime_type,
                    len(image_bytes),
                    _logs_json(logs),
                    str(input_path.relative_to(self.data_dir)),
                ),
            )

    def complete_success(
        self,
        *,
        session_id: str,
        image_bytes: bytes,
        mime_type: str,
        render_duration_ms: int,
        logs: Iterable[Any] = (),
    ) -> None:
        safe_id = _safe_session_id(session_id)
        extension = MIME_EXTENSIONS.get(mime_type, "bin")
        session_dir = self.media_dir / safe_id
        session_dir.mkdir(parents=True, exist_ok=True)
        output_path = session_dir / f"output.{extension}"
        output_path.write_bytes(image_bytes)
        completed_at = _utc_now()
        with self._lock, self._connection:
            self._connection.execute(
                """
                UPDATE sessions
                SET status = 'success',
                    completed_at = ?,
                    render_duration_ms = ?,
                    output_mime_type = ?,
                    output_byte_count = ?,
                    error_code = NULL,
                    error_message = NULL,
                    logs_json = ?,
                    output_path = ?
                WHERE id = ?
                """,
                (
                    completed_at,
                    max(0, int(render_duration_ms)),
                    mime_type,
                    len(image_bytes),
                    _logs_json(logs),
                    str(output_path.relative_to(self.data_dir)),
                    session_id,
                ),
            )

    def complete_failure(
        self,
        *,
        session_id: str,
        error_code: str,
        error_message: str,
        render_duration_ms: int,
        logs: Iterable[Any] = (),
    ) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                UPDATE sessions
                SET status = 'failed',
                    completed_at = ?,
                    render_duration_ms = ?,
                    error_code = ?,
                    error_message = ?,
                    logs_json = ?
                WHERE id = ?
                """,
                (
                    _utc_now(),
                    max(0, int(render_duration_ms)),
                    _clip(error_code, 120),
                    _clip(error_message, MAX_LOG_STRING_LENGTH),
                    _logs_json(logs),
                    session_id,
                ),
            )

    def list_sessions(
        self,
        *,
        page: int = 1,
        limit: int = 10,
        search: str = "",
        scenario_id: str = "",
        status: str = "",
    ) -> dict[str, Any]:
        page = max(1, min(int(page), 100_000))
        limit = max(1, min(int(limit), 50_000))
        where: list[str] = []
        params: list[Any] = []
        if search.strip():
            pattern = f"%{search.strip()}%"
            where.append(
                "(id LIKE ? COLLATE NOCASE OR scenario_id LIKE ? COLLATE NOCASE "
                "OR error_message LIKE ? COLLATE NOCASE)"
            )
            params.extend([pattern, pattern, pattern])
        if scenario_id.strip():
            where.append("scenario_id = ?")
            params.append(scenario_id.strip())
        if status.strip() in {"running", "success", "failed"}:
            where.append("status = ?")
            params.append(status.strip())

        where_sql = f"WHERE {' AND '.join(where)}" if where else ""
        with self._lock:
            total_row = self._connection.execute(
                f"SELECT COUNT(*) AS total FROM sessions {where_sql}", params
            ).fetchone()
            offset = (page - 1) * limit
            rows = self._connection.execute(
                f"""
                SELECT * FROM sessions
                {where_sql}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                [*params, limit, offset],
            ).fetchall()

        total_items = int(total_row["total"] if total_row else 0)
        total_pages = max(1, (total_items + limit - 1) // limit)
        return {
            "data": [self._serialize_session(row) for row in rows],
            "meta": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total_items,
            },
        }

    def get_image(self, session_id: str, variant: str) -> tuple[Path, str] | None:
        column = {"input": "input_path", "output": "output_path"}.get(variant)
        if column is None:
            return None
        with self._lock:
            row = self._connection.execute(
                f"SELECT {column}, {'input_mime_type' if variant == 'input' else 'output_mime_type'} AS mime_type "
                "FROM sessions WHERE id = ?",  # noqa: S608 - column is allow-listed.
                (session_id,),
            ).fetchone()
        if row is None or not row[column]:
            return None
        file_path = (self.data_dir / row[column]).resolve()
        try:
            file_path.relative_to(self.data_dir.resolve())
        except ValueError:
            return None
        if not file_path.is_file():
            return None
        return file_path, row["mime_type"] or "application/octet-stream"

    def overview(self) -> dict[str, Any]:
        with self._lock:
            rows = self._connection.execute("SELECT * FROM sessions ORDER BY created_at ASC").fetchall()

        total_jobs = len(rows)
        success_jobs = sum(row["status"] == "success" for row in rows)
        failed_jobs = sum(row["status"] == "failed" for row in rows)
        completed_jobs = success_jobs + failed_jobs
        durations = [int(row["render_duration_ms"] or 0) for row in rows if int(row["render_duration_ms"] or 0) > 0]
        scenario_counts: dict[str, int] = {}
        hourly_activity = [0] * 24
        now = datetime.now(timezone.utc)
        daily_keys: list[str] = []
        daily_values: dict[str, int] = {}
        for days_ago in range(13, -1, -1):
            date_value = (now - timedelta(days=days_ago)).astimezone(self.display_timezone)
            key = date_value.strftime("%d/%m")
            daily_keys.append(key)
            daily_values[key] = 0

        for row in rows:
            scenario_id = row["scenario_id"] or "unknown"
            scenario_counts[scenario_id] = scenario_counts.get(scenario_id, 0) + 1
            timestamp = _parse_timestamp(row["created_at"])
            if timestamp is None:
                continue
            local_timestamp = timestamp.astimezone(self.display_timezone)
            daily_key = local_timestamp.strftime("%d/%m")
            if daily_key in daily_values:
                daily_values[daily_key] += 1
            hourly_activity[local_timestamp.hour] += 1

        avg_render_time = round(sum(durations) / len(durations) / 1000, 1) if durations else 0
        success_rate = round((success_jobs / completed_jobs) * 100) if completed_jobs else 0
        error_rate = round((failed_jobs / completed_jobs) * 100) if completed_jobs else 0
        return {
            "ok": True,
            "total_jobs": total_jobs,
            "success_jobs": success_jobs,
            "failed_jobs": failed_jobs,
            "running_jobs": sum(row["status"] == "running" for row in rows),
            "success_rate": success_rate,
            "error_rate": error_rate,
            "avg_render_time": avg_render_time,
            "scenario_counts": scenario_counts,
            "trend_labels": daily_keys,
            "trend_values": [daily_values[key] for key in daily_keys],
            "hourly_activity": hourly_activity,
        }

    def _serialize_session(self, row: sqlite3.Row) -> dict[str, Any]:
        session_id = row["id"]
        input_url = f"/api/dashboard/sessions/{session_id}/image/input" if row["input_path"] else ""
        output_url = f"/api/dashboard/sessions/{session_id}/image/output" if row["output_path"] else ""
        return {
            "id": session_id,
            "name": "Guest group",
            "description": f"{row['people_count']} guest(s) · {row['scenario_id']}",
            "scenario_id": row["scenario_id"],
            "people_count": row["people_count"],
            "status": row["status"],
            "input_image_url": input_url,
            "output_image_url": output_url,
            "created_at": row["created_at"],
            "completed_at": row["completed_at"],
            "render_duration_ms": int(row["render_duration_ms"] or 0),
            "render_duration": round(int(row["render_duration_ms"] or 0) / 1000, 1),
            "input_mime_type": row["input_mime_type"] or "",
            "input_byte_count": int(row["input_byte_count"] or 0),
            "output_mime_type": row["output_mime_type"] or "",
            "output_byte_count": int(row["output_byte_count"] or 0),
            "error_code": row["error_code"] or "",
            "error_message": row["error_message"] or "",
            "logs": _parse_logs(row["logs_json"]),
        }


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_session_id(session_id: str) -> str:
    return SESSION_ID_PATTERN.sub("_", str(session_id))[:160] or "unknown"


def _clip(value: Any, limit: int = MAX_LOG_STRING_LENGTH) -> str:
    return str(value or "")[:limit]


def _normalize_logs(logs: Iterable[Any]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for raw_entry in list(logs or [])[-MAX_LOG_ENTRIES:]:
        if hasattr(raw_entry, "model_dump"):
            raw_entry = raw_entry.model_dump(mode="json")
        if not isinstance(raw_entry, dict):
            continue
        message = raw_entry.get("message")
        event = raw_entry.get("event")
        if not isinstance(message, str) or not message.strip() or not isinstance(event, str) or not event.strip():
            continue
        level = raw_entry.get("level")
        if level == "warn":
            level = "warning"
        if level not in {"info", "success", "warning", "error"}:
            level = "info"
        timestamp = raw_entry.get("timestamp")
        if not isinstance(timestamp, str) or _parse_timestamp(timestamp) is None:
            timestamp = _utc_now()
        details = raw_entry.get("details")
        normalized.append(
            {
                "timestamp": timestamp,
                "level": level,
                "event": _clip(event, 160),
                "message": _clip(message),
                "details": _safe_json(details) if isinstance(details, dict) else None,
            }
        )
    return normalized[-MAX_LOG_ENTRIES:]


def _logs_json(logs: Iterable[Any]) -> str:
    return json.dumps(_normalize_logs(logs), ensure_ascii=False)


def _parse_logs(value: Any) -> list[dict[str, Any]]:
    try:
        raw_logs = json.loads(value or "[]")
    except (TypeError, ValueError):
        return []
    return _normalize_logs(raw_logs)


def _safe_json(value: Any, depth: int = 0) -> Any:
    if depth > 5:
        return "[TRUNCATED]"
    if isinstance(value, dict):
        return {
            _clip(key, 120): _safe_json(item, depth + 1)
            for key, item in list(value.items())[:80]
        }
    if isinstance(value, list):
        return [_safe_json(item, depth + 1) for item in value[:80]]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return _clip(value) if isinstance(value, str) else value
    return _clip(value)


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
