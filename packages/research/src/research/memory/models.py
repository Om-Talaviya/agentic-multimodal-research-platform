"""Pydantic data models and schemas for Research Memory (Phase 16)."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field, model_validator


class MemoryType(str, Enum):
    """Categorization of persistent research memories."""

    FACT = "fact"
    CONCEPT = "concept"
    HYPOTHESIS = "hypothesis"
    FINDING = "finding"
    INSIGHT = "insight"
    METHODOLOGY = "methodology"
    SUMMARY = "summary"
    PREFERENCE = "preference"
    CONTRADICTION = "contradiction"


class MemoryItem(BaseModel):
    """A durable item of cross-session research knowledge."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: Optional[str] = None
    job_id: Optional[str] = None
    project_id: Optional[str] = None
    memory_type: MemoryType = MemoryType.FINDING
    title: str
    content: str
    confidence_score: float = Field(default=0.90, ge=0.0, le=1.0)
    confidence: Optional[float] = None
    tags: List[str] = Field(default_factory=list)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    source_type: str = "report"
    is_pinned: bool = False
    access_count: int = 0
    last_accessed_at: Optional[str] = None
    created_at: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def sync_confidence_fields(self) -> "MemoryItem":
        if self.confidence is not None:
            self.confidence_score = self.confidence
        else:
            self.confidence = self.confidence_score
        return self


class MemorySearchRequest(BaseModel):
    """Request model for querying research memory."""

    query: str
    memory_type: Optional[MemoryType] = None
    project_id: Optional[str] = None
    is_pinned: Optional[bool] = None
    tag: Optional[str] = None
    min_confidence: float = Field(default=0.70, ge=0.0, le=1.0)
    top_k: int = Field(default=5, ge=1, le=50)


class MemoryRecallResult(BaseModel):
    """Result of cross-session memory retrieval."""

    memories: List[MemoryItem] = Field(default_factory=list)
    total_found: int = 0
    total_recalled: int = 0
    query: str
    augmented_prompt_context: str = ""

    @model_validator(mode="after")
    def sync_total_counts(self) -> "MemoryRecallResult":
        if self.total_found == 0 and self.memories:
            self.total_found = len(self.memories)
        if self.total_recalled == 0:
            self.total_recalled = self.total_found
        return self
