"""Database engine, session factory, and dependency injection."""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine, event
from app.core.config import settings


# ─── Async engine (for API requests) ────────────────────────────
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    connect_args={
        "prepared_statement_cache_size": 0,  # Required for Supabase PgBouncer (asyncpg)
        "statement_cache_size": 0,           # Required for Supabase PgBouncer (asyncpg)
    },
)

async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ─── Sync engine (for seeding / migrations) ─────────────────────
sync_engine = create_engine(
    settings.DATABASE_URL_SYNC,
    echo=settings.DEBUG,
    pool_size=5,
    pool_pre_ping=True,
)

# Disable psycopg3 prepared statements for Supabase/PgBouncer
@event.listens_for(sync_engine, "connect")
def _set_pg_prepare_threshold(dbapi_conn, connection_record):
    if hasattr(dbapi_conn, "prepare_threshold"):
        dbapi_conn.prepare_threshold = 0


# ─── Base model ──────────────────────────────────────────────────
class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all models."""
    pass


# ─── Dependency ──────────────────────────────────────────────────
async def get_db() -> AsyncSession:
    """FastAPI dependency that provides an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
