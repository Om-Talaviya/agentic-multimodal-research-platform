"""Shared exception classes."""

from typing import Any


class ResearchError(Exception):
    """Base exception for research platform errors."""
    
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class ValidationError(ResearchError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: str | None = None, details: dict | None = None):
        super().__init__(message, code="VALIDATION_ERROR", details=details)
        if field:
            self.details["field"] = field


class NotFoundError(ResearchError):
    """Raised when a resource is not found."""
    
    def __init__(self, resource: str, identifier: str | int):
        super().__init__(
            f"{resource} not found: {identifier}",
            code="NOT_FOUND",
            details={"resource": resource, "identifier": str(identifier)},
        )


class ConflictError(ResearchError):
    """Raised when a resource conflict occurs."""
    
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="CONFLICT", details=details)


class ProviderError(ResearchError):
    """Raised when a model provider fails."""
    
    def __init__(self, provider: str, message: str, details: dict | None = None):
        super().__init__(
            f"Provider '{provider}' error: {message}",
            code="PROVIDER_ERROR",
            details={"provider": provider, **(details or {})},
        )


class ProviderUnavailableError(ProviderError):
    """Raised when a provider is unavailable."""
    
    def __init__(self, provider: str):
        super().__init__(provider, "Provider is unavailable", {"retryable": True})


class ModelNotFoundError(ProviderError):
    """Raised when a requested model is not available."""
    
    def __init__(self, provider: str, model: str):
        super().__init__(provider, f"Model not found: {model}", {"model": model})


class AgentError(ResearchError):
    """Raised when an agent execution fails."""
    
    def __init__(self, agent: str, message: str, details: dict | None = None):
        super().__init__(
            f"Agent '{agent}' error: {message}",
            code="AGENT_ERROR",
            details={"agent": agent, **(details or {})},
        )


class ToolError(ResearchError):
    """Raised when a tool execution fails."""
    
    def __init__(self, tool: str, message: str, details: dict | None = None):
        super().__init__(
            f"Tool '{tool}' error: {message}",
            code="TOOL_ERROR",
            details={"tool": tool, **(details or {})},
        )


class PlanningError(ResearchError):
    """Raised when research planning fails."""
    
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="PLANNING_ERROR", details=details)


class CircularDependencyError(ResearchError):
    """Raised when a circular dependency is detected in task graph."""
    
    def __init__(self, message: str = "Circular dependency detected in research plan"):
        super().__init__(message, code="CIRCULAR_DEPENDENCY")


class RateLimitError(ResearchError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, limit: int, window: int):
        super().__init__(
            f"Rate limit exceeded: {limit} requests per {window} seconds",
            code="RATE_LIMITED",
            details={"limit": limit, "window_seconds": window},
        )


class AuthenticationError(ResearchError):
    """Raised when user authentication fails."""

    def __init__(self, message: str = "Authentication failed", details: dict | None = None):
        super().__init__(message, code="AUTHENTICATION_ERROR", details=details)


class AuthorizationError(ResearchError):
    """Raised when user lacks required permission or role."""

    def __init__(self, message: str = "Permission denied", details: dict | None = None):
        super().__init__(message, code="AUTHORIZATION_ERROR", details=details)