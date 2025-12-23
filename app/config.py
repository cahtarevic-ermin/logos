from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Application
    app_name: str = "logos"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://logos:logos@localhost:5433/logos"
    database_url_sync: str = "postgresql+psycopg2://logos:logos@localhost:5433/logos"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Google AI
    google_api_key: str = ""

    # File Storage
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 50

    # Processing
    chunk_size: int = 1000
    chunk_overlap: int = 200
    embedding_model: str = "models/embedding-001"
    llm_model: str = "gemini-1.5-flash"

@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
