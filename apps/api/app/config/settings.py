from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Job Agent"
    app_env: str = "development"
    app_debug: bool = True

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/job_agent"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = "zUzgEqi0vYukxDCxvNsAKm0l8hjFXHSF2TcC8AX6vDY"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    storage_backend: str = "local"
    local_storage_path: str = "./storage"
    max_upload_bytes: int = 10 * 1024 * 1024

    cors_origins: str = "http://localhost:3000"

    job_ingest_scheduler_enabled: bool = False
    job_ingest_run_on_startup: bool = False
    job_ingest_hours: str = "6,18"
    job_ingest_board_delay_seconds: float = 0.2
    greenhouse_board_tokens: str = ""
    lever_sites: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() in {"development", "dev", "local"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
