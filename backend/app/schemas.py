from typing import Any, Literal

from pydantic import BaseModel


LogLevel = Literal["info", "success", "warning", "error"]


class LogEntry(BaseModel):
    timestamp: str
    level: LogLevel
    event: str
    message: str
    details: dict[str, Any] | None = None


class GenerationError(BaseModel):
    code: str
    message: str
    retryable: bool


class GenerationSuccessResponse(BaseModel):
    success: Literal[True] = True
    request_id: str
    result_image: str
    photo_publish_ticket: str = ""
    logs: list[LogEntry]


class GenerationErrorResponse(BaseModel):
    success: Literal[False] = False
    request_id: str
    error: GenerationError
    logs: list[LogEntry]


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    provider: Literal["gemini"] = "gemini"
    model: str
