"""LLM service layer for communicating with LLM providers."""

import logging

from app.config import Settings
from app.prompts.classification_prompt import (
    build_classification_system_prompt,
    build_classification_user_prompt,
)
from app.services.llm_base import BaseLLMProvider, LLMCompletionResult, create_llm_provider
from app.utils.exceptions import LLMServiceError
from app.utils.retry import retry_async

logger = logging.getLogger(__name__)

# LLMServiceError covers transient failures from any provider
RETRYABLE_EXCEPTIONS: tuple[type[Exception], ...] = (LLMServiceError,)

# Conditionally import OpenAI exceptions for providers that use the OpenAI SDK
try:
    from openai import APIConnectionError, APITimeoutError, RateLimitError
    RETRYABLE_EXCEPTIONS = (
        APIConnectionError,
        APITimeoutError,
        RateLimitError,
        LLMServiceError,
    )
except ImportError:
    pass


class LLMService:
    """Service for LLM API interactions, isolated from business logic."""

    def __init__(
        self,
        settings: Settings,
        provider: BaseLLMProvider | None = None,
    ) -> None:
        self._settings = settings
        self._provider = provider or create_llm_provider(settings)

    async def classify_ticket_raw(self, ticket: str) -> LLMCompletionResult:
        """
        Send a ticket to the LLM and return the raw completion result.

        Retries transient failures on the primary provider, then falls back to
        the configured fallback provider (Groq by default) if the primary fails.
        """
        system_prompt = build_classification_system_prompt()
        user_prompt = build_classification_user_prompt(ticket)

        async def _run(provider: BaseLLMProvider) -> LLMCompletionResult:
            return await retry_async(
                lambda: provider.complete(system_prompt, user_prompt),
                max_retries=self._settings.llm_max_retries,
                backoff_seconds=self._settings.llm_retry_backoff_seconds,
                retryable_exceptions=RETRYABLE_EXCEPTIONS,
            )

        try:
            return await _run(self._provider)
        except Exception as exc:
            fallback = self._create_fallback_provider()
            if fallback is None:
                logger.error("LLM service failed after retries: %s", exc)
                raise LLMServiceError(
                    "LLM service unavailable after multiple retries."
                ) from exc

            primary_name = self._settings.llm_provider.strip() or "primary"
            fallback_name = self._settings.llm_fallback_provider.strip()
            logger.warning(
                "Primary provider '%s' failed after retries: %s. "
                "Falling back to '%s'.",
                primary_name,
                exc,
                fallback_name,
            )
            try:
                return await _run(fallback)
            except Exception as fallback_exc:
                logger.error(
                    "Fallback provider '%s' also failed: %s",
                    fallback_name,
                    fallback_exc,
                )
                raise LLMServiceError(
                    f"Both '{primary_name}' and fallback '{fallback_name}' "
                    "failed after retries."
                ) from fallback_exc

    def _create_fallback_provider(self) -> BaseLLMProvider | None:
        """
        Build the configured fallback provider, or None if unavailable.

        Returns None when no fallback is configured, when the fallback is the
        same as the primary provider, or when the fallback has no API key.
        """
        fallback_name = self._settings.llm_fallback_provider.lower().strip()
        primary_name = self._settings.llm_provider.lower().strip()

        if not fallback_name or fallback_name == primary_name:
            return None

        try:
            provider = create_llm_provider(self._settings, fallback_name)
        except ValueError as exc:
            logger.error("Configured fallback provider is invalid: %s", exc)
            return None

        if not provider.is_configured():
            logger.warning(
                "Fallback provider '%s' is not configured (missing API key); "
                "skipping fallback.",
                fallback_name,
            )
            return None

        return provider
