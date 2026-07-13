"""Abstract LLM provider interface and factory."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.config import Settings


@dataclass
class LLMCompletionResult:
    """Standardized result from an LLM completion call."""

    content: str
    model: str
    provider: str


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def complete(self, system_prompt: str, user_prompt: str) -> LLMCompletionResult:
        """Generate a completion from system and user prompts."""

    def is_configured(self) -> bool:
        """Return True if the provider has the credentials it needs to run."""
        return True


def create_llm_provider(settings: Settings, provider_name: str | None = None) -> BaseLLMProvider:
    """
    Factory to create an LLM provider by name.

    Defaults to LLM_PROVIDER from the environment; pass ``provider_name`` to
    create a specific provider (e.g. the Groq fallback).
    """
    provider = (provider_name or settings.llm_provider).lower().strip()

    if provider == "gemini":
        from app.services.providers.gemini_provider import GeminiProvider

        return GeminiProvider(settings)

    if provider == "groq":
        from app.services.providers.groq_provider import GroqProvider

        return GroqProvider(settings)

    if provider == "openai":
        from app.services.providers.openai_provider import OpenAIProvider

        return OpenAIProvider(settings)

    raise ValueError(
        f"Unsupported LLM provider: '{provider}'. "
        "Supported providers: gemini, groq, openai"
    )
