"""AI Research OS Official Python SDK."""

from .client import AIResearchClient, ResearchService, DocumentService, UsageService
from .exceptions import (
    AIResearchOSError,
    AuthenticationError,
    RateLimitError,
    ResourceNotFoundError,
    ValidationError,
    APIError,
)
from .models import (
    ResearchJobCreateRequest,
    ResearchJobResponse,
    TaskStatus,
    SynthesisReport,
    DocumentIngestResponse,
    ApiUsageSummary,
)

__version__ = "1.1.0"

__all__ = [
    "AIResearchClient",
    "ResearchService",
    "DocumentService",
    "UsageService",
    "AIResearchOSError",
    "AuthenticationError",
    "RateLimitError",
    "ResourceNotFoundError",
    "ValidationError",
    "APIError",
    "ResearchJobCreateRequest",
    "ResearchJobResponse",
    "TaskStatus",
    "SynthesisReport",
    "DocumentIngestResponse",
    "ApiUsageSummary",
]
