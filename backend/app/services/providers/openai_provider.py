"""OpenAI LLM provider implementation."""

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


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider for ticket classification."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: AsyncOpenAI | None = None

    def is_configured(self) -> bool:
        """Return True if an OpenAI API key is set."""
        return bool(self._settings.openai_api_key)

    def _get_client(self) -> AsyncOpenAI:
        """Lazily initialize the OpenAI client."""
        if not self._settings.openai_api_key:
            raise ConfigurationError(
                "OPENAI_API_KEY is not configured.",
                "Set it in your .env file.",
            )
        if self._client is None:
            client_kwargs: dict = {"api_key": self._settings.openai_api_key}
            if self._settings.openai_base_url:
                client_kwargs["base_url"] = self._settings.openai_base_url
            self._client = AsyncOpenAI(**client_kwargs)
        return self._client

    async def complete(self, system_prompt: str, user_prompt: str) -> LLMCompletionResult:
        """Call OpenAI chat completions API."""
        client = self._get_client()
        try:
            response = await client.chat.completions.create(
                model=self._settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
                timeout=self._settings.llm_timeout_seconds,
            )
        except RETRYABLE_EXCEPTIONS as exc:
            logger.error("OpenAI API transient error: %s", exc)
            raise
        except Exception as exc:
            logger.error("OpenAI API error: %s", exc)
            raise LLMServiceError(f"OpenAI API error: {exc}") from exc

        if not response.choices:
            raise LLMServiceError("OpenAI returned an empty response.")

        content = response.choices[0].message.content or ""
        if not content.strip():
            raise LLMServiceError("OpenAI returned empty content.")

        return LLMCompletionResult(
            content=content,
            model=self._settings.openai_model,
            provider="openai",
        )
