"""Shared test fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app
from app.services.classifier_service import ClassifierService
from app.services.llm_base import LLMCompletionResult
from app.services.llm_service import LLMService


class MockLLMProvider:
    """Mock LLM provider for unit tests."""

    def __init__(self, response_content: str) -> None:
        self.response_content = response_content
        self.calls: list[tuple[str, str]] = []

    async def complete(self, system_prompt: str, user_prompt: str) -> LLMCompletionResult:
        self.calls.append((system_prompt, user_prompt))
        return LLMCompletionResult(
            content=self.response_content,
            model="mock-model",
            provider="mock",
        )


@pytest.fixture
def test_settings() -> Settings:
    """Return isolated test settings with dummy keys (ignores the real .env)."""
    return Settings(
        _env_file=None,  # do not load the developer's real .env / API keys
        gemini_api_key="test-key",
        gemini_model="gemini-pro",
        confidence_threshold=0.60,
        llm_max_retries=1,
    )


@pytest.fixture
def client() -> TestClient:
    """Return FastAPI test client."""
    return TestClient(app)


def build_classifier(
    settings: Settings,
    llm_response: str,
) -> ClassifierService:
    """Build a classifier service with a mocked LLM provider."""
    mock_provider = MockLLMProvider(llm_response)
    llm_service = LLMService(settings=settings, provider=mock_provider)
    return ClassifierService(llm_service=llm_service, settings=settings)
