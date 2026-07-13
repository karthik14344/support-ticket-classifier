"""Gemini LLM provider implementation using the official Google GenAI SDK."""

import json
import logging

from google import genai
from google.genai import types

from app.config import Settings
from app.services.llm_base import BaseLLMProvider, LLMCompletionResult
from app.utils.exceptions import ConfigurationError, LLMServiceError

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """Gemini API provider for ticket classification."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: genai.Client | None = None

    def is_configured(self) -> bool:
        """Return True if a Gemini API key is set."""
        return bool(self._settings.gemini_api_key)

    def _get_client(self) -> genai.Client:
        """Lazily initialize the Gemini client."""
        if not self._settings.gemini_api_key:
            raise ConfigurationError(
                "GEMINI_API_KEY is not configured.",
                "Set it in your .env file.",
            )
        if self._client is None:
            self._client = genai.Client(api_key=self._settings.gemini_api_key)
        return self._client

    async def complete(self, system_prompt: str, user_prompt: str) -> LLMCompletionResult:
        """Call the Gemini API via the official Google GenAI SDK."""
        client = self._get_client()
        try:
            response = await client.aio.models.generate_content(
                model=self._settings.gemini_model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.0,
                    response_mime_type="application/json",
                ),
            )
        except Exception as exc:
            error_msg = str(exc).lower()
            if any(
                keyword in error_msg
                for keyword in ("timeout", "deadline", "connect", "rate", "quota", "resource_exhausted")
            ):
                logger.error("Gemini API transient error: %s", exc)
                raise LLMServiceError(f"Gemini API transient error: {exc}") from exc
            logger.error("Gemini API error: %s", exc)
            raise LLMServiceError(f"Gemini API error: {exc}") from exc

        if not response or not response.text:
            raise LLMServiceError("Gemini returned an empty response.")

        content = response.text.strip()
        if not content:
            raise LLMServiceError("Gemini returned empty content.")

        return LLMCompletionResult(
            content=content,
            model=self._settings.gemini_model,
            provider="gemini",
        )
