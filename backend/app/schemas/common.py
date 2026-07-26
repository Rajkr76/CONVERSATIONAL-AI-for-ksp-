"""Common/shared schemas."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    version: str
    database: str = "connected"


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    error_code: str = "UNKNOWN_ERROR"
