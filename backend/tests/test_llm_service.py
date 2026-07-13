"""Tests for LLM service error handling."""

import pytest
from openai import APITimeoutError

from app.services.llm_service import LLMService
from app.utils.exceptions import LLMServiceError
from tests.conftest import MockLLMProvider


class FailingProvider:
    """Provider that always raises timeout errors."""

    async def complete(self, system_prompt: str, user_prompt: str):
        raise APITimeoutError(request=None)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_llm_service_retries_and_raises(test_settings) -> None:
    """LLM service should retry and raise LLMServiceError after exhaustion."""
    test_settings.llm_max_retries = 2
    llm_service = LLMService(settings=test_settings, provider=FailingProvider())

    with pytest.raises(LLMServiceError, match="unavailable after multiple retries"):
        await llm_service.classify_ticket_raw("Test ticket")


@pytest.mark.asyncio
async def test_llm_service_success(test_settings) -> None:
    """LLM service should return completion on success."""
    provider = MockLLMProvider('{"category": "Account", "confidence": 0.9}')
    llm_service = LLMService(settings=test_settings, provider=provider)

    result = await llm_service.classify_ticket_raw("How do I change my email?")

    assert "Account" in result.content
    assert len(provider.calls) == 1
