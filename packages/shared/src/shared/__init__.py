"""Shared utilities for Agentic Multimodal Research Platform."""

from shared.config import settings
from shared.logging import get_logger, setup_logging
from shared.exceptions import (
    ResearchError,
    ValidationError,
    NotFoundError,
    ProviderError,
    AgentError,
    AuthenticationError,
    AuthorizationError,
)
from shared.auth import (
    User,
    UserRole,
    TokenPayload,
    TokenResponse,
    LoginRequest,
    TokenRefreshRequest,
    create_access_token,
    create_refresh_token,
    verify_token,
    hash_password,
    verify_password,
    user_registry,
)
from shared.security import (
    validate_user_prompt,
    check_prompt_injection,
    sanitize_text,
    is_safe_filename,
    sanitize_log_dict,
)
from shared.types import JSONDict, UUIDStr

__all__ = [
    "settings",
    "get_logger",
    "setup_logging",
    "ResearchError",
    "ValidationError",
    "NotFoundError",
    "ProviderError",
    "AgentError",
    "JSONDict",
    "UUIDStr",
    "User",
    "UserRole",
    "TokenPayload",
    "TokenResponse",
    "LoginRequest",
    "TokenRefreshRequest",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "hash_password",
    "verify_password",
    "user_registry",
    "validate_user_prompt",
    "check_prompt_injection",
    "sanitize_text",
    "is_safe_filename",
    "sanitize_log_dict",
]