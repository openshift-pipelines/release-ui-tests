"""Retry helpers for eventually-consistent UI assertions."""

from __future__ import annotations

import functools
import logging
import time
from typing import Callable, TypeVar

logger = logging.getLogger(__name__)

R = TypeVar("R")


def _log_retry(name: str, attempt: int, retries: int, error: BaseException, delay: float) -> None:
    logger.info(
        "%s attempt %s/%s failed (%s); retrying in %.1fs",
        name,
        attempt,
        retries,
        error,
        delay,
    )


def _call_with_retries(
    func: Callable[..., R],
    args: tuple[object, ...],
    kwargs: dict[str, object],
    retries: int,
    delay_seconds: float,
    exceptions: tuple[type[BaseException], ...],
    backoff: float,
) -> R:
    delay = delay_seconds
    last_error: BaseException | None = None
    for attempt in range(1, retries + 1):
        try:
            return func(*args, **kwargs)
        except exceptions as error:
            last_error = error
            if attempt == retries:
                break
            _log_retry(func.__name__, attempt, retries, error, delay)
            time.sleep(delay)
            delay *= backoff
    assert last_error is not None
    raise last_error


def retry_on_exception(
    retries: int = 3,
    delay_seconds: float = 2.0,
    exceptions: tuple[type[BaseException], ...] = (AssertionError,),
    backoff: float = 1.0,
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Retry a sync callable when it raises one of ``exceptions``.

    Use for UI checks that can lag behind a save (labels, annotation counts).
    Does not swallow the final failure — the last exception is re-raised.

    :param retries: Total attempts, including the first try
    :param delay_seconds: Base wait between attempts
    :param exceptions: Exception types that trigger another attempt
    :param backoff: Multiplier applied to the delay after each failed attempt
                    (1.0 = fixed delay, 2.0 = exponential)
    """
    if retries < 1:
        raise ValueError("retries must be >= 1")

    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> R:
            return _call_with_retries(func, args, kwargs, retries, delay_seconds, exceptions, backoff)

        return wrapper

    return decorator
