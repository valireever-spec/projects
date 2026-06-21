"""
Structured JSON logging configuration for investing-platform V-Model tracker.

Provides JSON-formatted logs with contextual fields for better observability:
- request_id, duration, status codes, error details
- Integrates with ELK stack, Datadog, CloudWatch
"""

import logging
import json
import sys
import time
from typing import Any, Dict, Optional
from datetime import datetime
from pythonjsonlogger import jsonlogger


class ContextFilter(logging.Filter):
    """Add contextual fields to log records."""

    def __init__(self) -> None:
        super().__init__()
        self.request_id: Optional[str] = None
        self.duration_ms: Optional[float] = None
        self.user_id: Optional[str] = None

    def filter(self, record: logging.LogRecord) -> bool:
        """Add context fields to log record."""
        if self.request_id:
            record.request_id = self.request_id  # type: ignore
        if self.duration_ms:
            record.duration_ms = self.duration_ms  # type: ignore
        if self.user_id:
            record.user_id = self.user_id  # type: ignore
        record.timestamp = datetime.utcnow().isoformat()  # type: ignore
        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields."""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any]
    ) -> None:
        """Add custom fields to JSON log.

        Args:
            log_record: Log record dict to add fields to
            record: Original logging record
            message_dict: Message dict from logger
        """
        super().add_fields(log_record, record, message_dict)

        # Add standard fields
        log_record["timestamp"] = datetime.utcnow().isoformat()
        log_record["logger"] = record.name
        log_record["level"] = record.levelname
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno

        # Add optional context fields if present
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id  # type: ignore
        if hasattr(record, "duration_ms"):
            log_record["duration_ms"] = record.duration_ms  # type: ignore
        if hasattr(record, "user_id"):
            log_record["user_id"] = record.user_id  # type: ignore

        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: Optional[str] = None
) -> logging.Logger:
    """Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: "json" for JSON format, "text" for human-readable
        log_file: Optional file to write logs to

    Returns:
        Configured root logger
    """
    logger: logging.Logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Add context filter
    context_filter = ContextFilter()
    logger.addFilter(context_filter)

    # Console handler
    console_handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)

    if log_format.lower() == "json":
        formatter = CustomJsonFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler: logging.FileHandler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Suppress third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    return logger


class LogContext:
    """Context manager for adding request context to logs."""

    def __init__(
        self,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> None:
        """Initialize log context.

        Args:
            request_id: Request ID for tracing
            user_id: User ID for multi-tenant contexts
        """
        self.request_id = request_id
        self.user_id = user_id
        self.start_time: float = time.time()
        self.logger = logging.getLogger(__name__)

    def __enter__(self) -> "LogContext":
        """Enter context."""
        # Update global context
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            for filter_ in handler.filters:
                if isinstance(filter_, ContextFilter):
                    filter_.request_id = self.request_id
                    filter_.user_id = self.user_id
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context and log duration."""
        duration_ms = (time.time() - self.start_time) * 1000
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            for filter_ in handler.filters:
                if isinstance(filter_, ContextFilter):
                    filter_.duration_ms = duration_ms

        if exc_type:
            self.logger.error(
                f"Context exited with exception after {duration_ms:.2f}ms",
                exc_info=(exc_type, exc_val, exc_tb)
            )
        else:
            self.logger.debug(f"Context completed in {duration_ms:.2f}ms")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module.

    Args:
        name: Module name (__name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
