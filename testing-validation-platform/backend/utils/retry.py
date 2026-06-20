"""
Retry utilities with exponential backoff for tracker API calls.
"""

import time
import logging
from typing import Callable, TypeVar, Any
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar("T")


def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: int = 2,
    backoff_multiplier: float = 2.0,
    max_delay: int = 60,
):
    """
    Decorator for retry with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts (default: 3)
        initial_delay: Initial delay between retries in seconds (default: 2)
        backoff_multiplier: Multiplier for exponential backoff (default: 2.0)
        max_delay: Maximum delay between retries in seconds (default: 60)

    Example:
        @retry_with_backoff(max_attempts=3, initial_delay=2)
        def api_call():
            return requests.get(...)
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    logger.debug(f"Attempt {attempt}/{max_attempts} for {func.__name__}")
                    result = func(*args, **kwargs)
                    if attempt > 1:
                        logger.info(f"✅ {func.__name__} succeeded on attempt {attempt}")
                    return result

                except Exception as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(
                            f"❌ {func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise

                    # Calculate delay for next attempt
                    logger.warning(
                        f"⚠️ {func.__name__} failed (attempt {attempt}/{max_attempts}), "
                        f"retrying in {delay}s: {e}"
                    )
                    time.sleep(delay)

                    # Exponential backoff
                    delay = min(int(delay * backoff_multiplier), max_delay)

            # This should never be reached, but just in case
            raise last_exception

        return wrapper

    return decorator


def call_with_retry(
    func: Callable[..., T],
    *args: Any,
    max_attempts: int = 3,
    initial_delay: int = 2,
    **kwargs: Any,
) -> T:
    """
    Call a function with retry logic (non-decorator approach).

    Args:
        func: Function to call
        *args: Positional arguments for func
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay between retries
        **kwargs: Keyword arguments for func

    Returns:
        Result of func call if successful

    Raises:
        Last exception if all retries fail
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(1, max_attempts + 1):
        try:
            logger.debug(f"Attempt {attempt}/{max_attempts} for {func.__name__}")
            result = func(*args, **kwargs)
            if attempt > 1:
                logger.info(f"✅ {func.__name__} succeeded on attempt {attempt}")
            return result

        except Exception as e:
            last_exception = e
            if attempt == max_attempts:
                logger.error(
                    f"❌ {func.__name__} failed after {max_attempts} attempts: {e}"
                )
                raise

            logger.warning(
                f"⚠️ {func.__name__} failed (attempt {attempt}/{max_attempts}), "
                f"retrying in {delay}s: {e}"
            )
            time.sleep(delay)
            delay = min(int(delay * 2), 60)  # Exponential backoff, max 60s

    # This should never be reached
    if last_exception:
        raise last_exception
    raise RuntimeError(f"Failed to call {func.__name__}")
