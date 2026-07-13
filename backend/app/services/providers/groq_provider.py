"""Groq LLM provider implementation."""

import logging

from openai import APIConnectionError, APITimeoutError, AsyncOpenAI, RateLimitError

from app.config import Settings
from app.services.llm_base import BaseLLMProvider, LLMCompletionResult
from app.utils.exceptions import ConfigurationError, LLMServiceError

logger = logging.getLogger(__name__)

RETRYABLE_EXCEPTIONS = (
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
)

# Groq uses an OpenAI-compatible API at api.groq.com
GROQ_DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"


class GroqProvider(BaseLLMProvider):
    """Groq API provider for ticket classification."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: AsyncOpenAI | None = None

    def is_configured(self) -> bool:
        """Return True if a Groq API key is set."""
        return bool(self._settings.groq_api_key)

    def _get_client(self) -> AsyncOpenAI:
        """Lazily initialize the Groq client."""
        if not self._settings.groq_api_key:
            raise ConfigurationError(
                "GROQ_API_KEY is not configured.",
                "Set it in your .env file.",
            )
        if self._client is None:
            base_url = self._settings.groq_base_url or GROQ_DEFAULT_BASE_URL
            self._client = AsyncOpenAI(
                api_key=self._settings.groq_api_key,
                base_url=base_url,
            )
        return self._client

    async def complete(self, system_prompt: str, user_prompt: str) -> LLMCompletionResult:
        """Call the Groq chat completion API."""
        client = self._get_client()
        try:
            response = await client.chat.completions.create(
                model=self._settings.groq_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
                timeout=self._settings.llm_timeout_seconds,
            )
        except RETRYABLE_EXCEPTIONS as exc:
            logger.error("Groq API transient error: %s", exc)
            raise
        except Exception as exc:
            logger.error("Groq API error: %s", exc)
            raise LLMServiceError(f"Groq API error: {exc}") from exc

        if not response.choices:
            raise LLMServiceError("Groq returned an empty response.")

        content = response.choices[0].message.content or ""
        if not content.strip():
            raise LLMServiceError("Groq returned empty content.")

        return LLMCompletionResult(
            content=content,
            model=self._settings.groq_model,
            provider="groq",
        )
