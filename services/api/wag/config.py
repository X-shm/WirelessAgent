"""Application configuration via environment variables."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # App
    app_name: str = "WirelessAgent"
    debug: bool = False
    secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours

    # Database (dev: SQLite; prod: PostgreSQL, e.g. postgresql+asyncpg://...)
    database_url: str = "sqlite+aiosqlite:///./wirelessagent.db"

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Worker
    task_poll_interval: float = 1.0


settings = Settings()