"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import async_engine, Base
from app.api.routes import chat, auth, history, export


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup: create tables if they don't exist
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(f"[{settings.APP_NAME}] v{settings.APP_VERSION} started")
    yield
    # Shutdown
    await async_engine.dispose()
    print("[Application] Shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered crime investigation assistant for Karnataka State Police",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── CORS Middleware ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routes ──────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(export.router, prefix="/api")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    from app.services.llm_service import llm_service
    ollama_ok = await llm_service.check_health()
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "ollama": "connected" if ollama_ok else "disconnected",
    }
