"""Retry utilities for transient failures."""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def retry_async(
    func: Callable[[], Awaitable[T]],
    *,
    max_retries: int,
    backoff_seconds: float,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> T:
    """
    Execute an async callable with exponential backoff retries.

    Args:
        func: Async callable to execute.
        max_retries: Maximum number of attempts.
        backoff_seconds: Initial backoff delay in seconds.
        retryable_exceptions: Exception types that trigger a retry.

    Returns:
        Result of the successful callable invocation.

    Raises:
        The last exception if all retries are exhausted.
    """
    last_exception: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            return await func()
        except retryable_exceptions as exc:
            last_exception = exc
            if attempt == max_retries:
                break
            delay = backoff_seconds * (2 ** (attempt - 1))
            logger.warning(
                "Attempt %d/%d failed: %s. Retrying in %.1fs.",
                attempt,
                max_retries,
                exc,
                delay,
            )
            await asyncio.sleep(delay)

    assert last_exception is not None
    raise last_exception
