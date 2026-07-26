"""Pydantic schemas for authentication."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Login credentials."""
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=100)


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserInfo"


class UserInfo(BaseModel):
    """Public user information."""
    id: UUID
    username: str
    full_name: str
    email: str
    role: str
    badge_number: Optional[str] = None
    department: Optional[str] = None


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    username: str = Field(..., min_length=3, max_length=100)
    email: str
    password: str = Field(..., min_length=6)
    full_name: str
    role: str = "officer"
    badge_number: Optional[str] = None
    department: Optional[str] = None


# Resolve forward reference
TokenResponse.model_rebuild()
