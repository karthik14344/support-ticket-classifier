"""FastAPI dependency injection providers."""

from functools import lru_cache

from app.config import Settings, get_settings
from app.services.classifier_service import ClassifierService
from app.services.llm_service import LLMService


@lru_cache
def get_llm_service() -> LLMService:
    """Return cached LLM service instance."""
    settings = get_settings()
    return LLMService(settings=settings)


def get_classifier_service() -> ClassifierService:
    """Return classifier service with injected dependencies."""
    settings = get_settings()
    llm_service = get_llm_service()
    return ClassifierService(llm_service=llm_service, settings=settings)


def get_app_settings() -> Settings:
    """Return application settings."""
    return get_settings()
