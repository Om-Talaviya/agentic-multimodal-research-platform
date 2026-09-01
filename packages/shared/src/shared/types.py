"""Shared type definitions."""

from typing import Any, TypeVar, Generic
from uuid import UUID
from datetime import datetime, timezone
from pydantic import BaseModel, Field


# Type aliases
JSONDict = dict[str, Any]
JSONList = list[Any]
UUIDStr = str


# Generic types
T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    
    items: list[T]
    total: int
    limit: int
    offset: int
    
    @property
    def has_more(self) -> bool:
        return self.offset + self.limit < self.total


class TimestampMixin(BaseModel):
    """Mixin for created/updated timestamps."""
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IDMixin(BaseModel):
    """Mixin for UUID primary key."""
    
    id: UUIDStr = Field(default_factory=lambda: str(UUID(int=0)))


# API Response types
class ErrorResponse(BaseModel):
    """Standard error response."""
    
    error: dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str
    version: str
    checks: dict[str, str]


# Common enums
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DocumentFormat(str, Enum):
    TEXT = "text"
    MARKDOWN = "markdown"
    PDF = "pdf"
    DOCX = "docx"
    IMAGE = "image"
    HTML = "html"
    UNKNOWN = "unknown"


class SourceType(str, Enum):
    WEB = "web"
    DOCUMENT = "document"
    PDF = "pdf"
    IMAGE = "image"
    DATABASE = "database"
    API = "api"


class VerificationStatus(str, Enum):
    UNVERIFIED = "unverified"
    SINGLE_SOURCE = "single_source"
    CONSENSUS = "consensus"
    CONFLICT = "conflict"
    PARTIAL = "partial"