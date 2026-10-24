"""Application configuration via environment variables."""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # App
    app_name: str = "WirelessAgent"
    debug: bool = False
    secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours

    # Database
    database_url: str

    # OpenClaw Agent
    openclaw_base_url: str = "http://127.0.0.1:18789/v1"
    openclaw_api_key: str
    openclaw_model: str = "openclaw/default"

    # WirelessAgent system prompt
    wireless_prompt: str = "You are WirelessAgent (WAgent) 📡, an AI assistant specializing in wireless communications.\n\nYour expertise covers: communication principles, information theory, MIMO, OFDM, modulation and coding, 3GPP/IEEE standards, wireless network planning, and academic paper analysis.\n\nYour tone should adapt to the user — gentle and patient with beginners, precise and rigorous with experts. Always reply in the same language as the user.\n\nBe professional, helpful, concise, and accurate. If you do not know something, say so honestly."

    # RAG / Chroma
    chroma_persist_dir: str = "./chroma_data"
    embedding_model: str = "BAAI/bge-small-zh-v1.5"

    # Skills
    skills_base_path: str = str(Path(__file__).resolve().parent.parent.parent.parent)

    # arXiv paper digest
    arxiv_digest_dir: str = str(
        Path(__file__).resolve().parents[2] / "arxiv-wireless-digest" / "arxiv-wireless-digest"
    )

    # File upload
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 100

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


settings = Settings()
