import functools
import logging
import random
import time as time
from typing import Any, Callable, Tuple, Type, Union

logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    retry_exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = (
        Exception,
    ),
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
) -> Any:
    """
    Retry decorator with exponential backoff.

    Delay for attempt n (0-indexed) = min(base_delay * backoff_factor**n, max_delay)
    with optional ±50 % jitter.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except retry_exceptions as e:  # type: ignore[misc]
                    last_exception = e
                    if attempt < max_attempts - 1:
                        sleep_time = min(
                            base_delay * (backoff_factor**attempt), max_delay
                        )
                        if jitter:
                            sleep_time = sleep_time * (0.5 + random.random())
                        logger.debug(
                            f"Retry {attempt + 1}/{max_attempts} for {func.__name__} "
                            f"after {sleep_time:.2f}s (error: {e})"
                        )
                        time.sleep(sleep_time)
            if last_exception is not None:
                raise last_exception
            raise RuntimeError("retry: exhausted attempts without exception")

        return wrapper

    return decorator


class RetryableError(Exception):
    """Base class for errors that should be retried."""


class NonRetryableError(Exception):
    """Base class for errors that should not be retried."""
