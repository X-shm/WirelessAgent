import os


class Settings:
    """后端配置：全部可用环境变量覆盖，生产用 PostgreSQL，开发用 SQLite 兜底。"""

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite+aiosqlite:///./wirelessagent.db"
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    TOKEN_TTL_SECONDS: int = int(os.getenv("TOKEN_TTL_SECONDS", "604800"))  # 7 天
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")


settings = Settings()