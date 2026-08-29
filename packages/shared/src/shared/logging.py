"""Structured logging configuration using structlog."""

import sys
import structlog
from structlog.types import Processor
from shared.config import settings


def sanitize_log_data(data: dict) -> dict:
    """Remove sensitive data from log entries."""
    sensitive_keys = {
        "api_key", "secret", "password", "token", "authorization",
        "credit_card", "ssn", "private_key", "access_token",
        "refresh_token", "bearer", "cookie", "password",
    }
    
    def _sanitize(obj):
        if isinstance(obj, dict):
            return {
                k: "[REDACTED]" if any(s in k.lower() for s in sensitive_keys) else _sanitize(v)
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [_sanitize(item) for item in obj]
        return obj
    
    return _sanitize(data)


def add_sanitized_data(logger, method_name, event_dict):
    """Processor to sanitize log data."""
    return sanitize_log_data(event_dict)


def setup_logging() -> None:
    """Configure structlog for the application."""
    
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        add_sanitized_data,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
    ]
    
    if settings.log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(structlog, settings.log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)