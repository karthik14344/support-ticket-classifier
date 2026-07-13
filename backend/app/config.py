"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    openai_base_url: Optional[str] = None
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    gemini_base_url: Optional[str] = None
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_base_url: Optional[str] = None
    llm_provider: str = "gemini"
    llm_fallback_provider: str = "groq"
    port: int = 8000
    host: str = "0.0.0.0"
    confidence_threshold: float = 0.60
    llm_timeout_seconds: float = 30.0
    llm_max_retries: int = 3
    llm_retry_backoff_seconds: float = 1.0
    log_level: str = "INFO"
    app_name: str = "Support Ticket Classifier API"
    app_version: str = "1.0.0"
    app_description: str = (
        "AI-powered support ticket classification using LLM APIs."
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
