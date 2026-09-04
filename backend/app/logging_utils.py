from datetime import datetime, timezone
from typing import Any

from .schemas import LogEntry, LogLevel


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class RequestLogger:
    def __init__(self) -> None:
        self._entries: list[LogEntry] = []

    # Only pass safe, explicitly selected details to this method.
    def add(
        self,
        level: LogLevel,
        event: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self._entries.append(
            LogEntry(
                timestamp=_timestamp(),
                level=level,
                event=event,
                message=message,
                details=details,
            )
        )

    def entries(self) -> list[LogEntry]:
        return list(self._entries)
