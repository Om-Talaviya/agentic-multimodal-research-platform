"""Exception definitions for AI Research OS SDK."""


class AIResearchOSError(Exception):
    """Base exception for all AI Research OS SDK errors."""
    pass


class AuthenticationError(AIResearchOSError):
    """Raised when the API key or authentication token is invalid or missing."""
    pass


class RateLimitError(AIResearchOSError):
    """Raised when the API rate limit has been exceeded."""
    pass


class ResourceNotFoundError(AIResearchOSError):
    """Raised when the requested job, document, or entity is not found."""
    pass


class ValidationError(AIResearchOSError):
    """Raised when input parameters fail schema validation."""
    pass


class APIError(AIResearchOSError):
    """Raised when the API returns an unhandled HTTP status code."""

    def __init__(self, status_code: int, detail: str, payload: dict | None = None) -> None:
        super().__init__(f"API Error ({status_code}): {detail}")
        self.status_code = status_code
        self.detail = detail
        self.payload = payload or {}
