from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Bank Phase 1"
    app_host: str = "127.0.0.1"
    app_port: int = 8000

    database_url: str = "postgresql+psycopg://ai_bank:ai_bank_password@localhost:5432/ai_bank"

    api_base_url: str = "http://127.0.0.1:8000"
    log_level: str = "INFO"

    groq_api_key: str
    groq_model: str = "openai/gpt-oss-120b"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings():
    return Settings()