"""Custom exception classes for the application."""

from typing import Optional


class AppError(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class LLMServiceError(AppError):
    """Raised when the LLM provider fails after retries."""

    def __init__(self, message: str = "LLM service unavailable.") -> None:
        super().__init__(message=message, status_code=503)


class LLMResponseError(AppError):
    """Raised when the LLM returns an invalid or unparseable response."""

    def __init__(
        self,
        message: str = "Invalid response from LLM.",
        status_code: int = 502,
    ) -> None:
        super().__init__(message=message, status_code=status_code)


class ClassificationError(AppError):
    """Raised when classification business logic fails."""

    def __init__(
        self,
        message: str = "Classification failed.",
        status_code: int = 500,
    ) -> None:
        super().__init__(message=message, status_code=status_code)


class ConfigurationError(AppError):
    """Raised when required configuration is missing."""

    def __init__(self, message: str, detail: Optional[str] = None) -> None:
        full_message = message if not detail else f"{message} {detail}"
        super().__init__(message=full_message, status_code=500)
