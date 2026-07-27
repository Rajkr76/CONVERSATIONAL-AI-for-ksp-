"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings via Pydantic BaseSettings."""

    # ─── App ─────────────────────────────────────────────────────
    APP_NAME: str = "KSP Crime Intelligence Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ─── Database ────────────────────────────────────────────────
    DATABASE_URL: str = (
        "postgresql+asyncpg://ksp_admin:ksp_secure_2024@localhost:5432/ksp_crime_db"
    )
    DATABASE_URL_SYNC: str = (
        "postgresql+psycopg://ksp_admin:ksp_secure_2024@localhost:5432/ksp_crime_db"
    )

    # ─── LLM Settings ────────────────────────────────────────────
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_PORT: int = 11434
    SQL_MODEL: str = "sqlcoder"
    ANSWER_MODEL: str = "llama3.1:8b"
    LLM_API_KEY: str | None = None


    # ─── JWT ─────────────────────────────────────────────────────
    JWT_SECRET: str = "ksp-hackathon-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 480

    # ─── CORS ────────────────────────────────────────────────────
    CORS_ORIGINS: str = "https://conversational-ai-by-cybershield.onslate.in"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ("../.env", ".env")
        case_sensitive = True
        extra = "ignore"


settings = Settings()
