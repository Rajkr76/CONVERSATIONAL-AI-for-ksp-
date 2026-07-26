"""Shared dependencies for API routes."""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.core.database import get_db
from app.core.security import get_current_user


async def get_database_session(
    db: AsyncSession = Depends(get_db),
) -> AsyncSession:
    """Alias for database session dependency."""
    return db


async def get_authenticated_user(
    user: dict = Depends(get_current_user),
) -> dict:
    """Alias for authenticated user dependency."""
    return user
