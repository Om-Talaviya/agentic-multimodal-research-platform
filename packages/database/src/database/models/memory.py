"""Database model for persistent cross-session research memory."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import CHAR, JSON, TypeDecorator
from database.connection import Base


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36).
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID())
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)


JSONType = JSON().with_variant(JSONB, "postgresql")


class DBResearchMemory(Base):
    """Persistent conceptual research memory capturing facts, concepts, hypotheses, findings, and preferences."""

    __tablename__ = "research_memories"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID, ForeignKey("research_jobs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    project_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # Memory classification: fact, concept, hypothesis, finding, preference, contradiction
    memory_type: Mapped[str] = mapped_column(String(50), nullable=False, default="finding", index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.90)

    # Conceptual indexing tags & provenance
    tags: Mapped[List[str]] = mapped_column(JSONType, nullable=False, default=list)
    provenance_json: Mapped[Dict[str, Any]] = mapped_column(JSONType, nullable=False, default=dict)

    @property
    def confidence(self) -> float:
        return self.confidence_score

    @confidence.setter
    def confidence(self, val: float) -> None:
        self.confidence_score = val

    @property
    def source_type(self) -> str:
        if isinstance(self.provenance_json, dict):
            return self.provenance_json.get("source", "report")
        return "report"

    # Lifecycle & relevance metadata
    is_pinned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    access_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user = relationship("User", backref="memories")
    job = relationship("ResearchJob", backref="extracted_memories")

    def to_dict(self) -> Dict[str, Any]:
        """Convert database model to serializable dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "job_id": str(self.job_id) if self.job_id else None,
            "project_id": self.project_id,
            "memory_type": self.memory_type,
            "title": self.title,
            "content": self.content,
            "confidence_score": self.confidence_score,
            "tags": self.tags if isinstance(self.tags, list) else [],
            "provenance": self.provenance_json if isinstance(self.provenance_json, dict) else {},
            "is_pinned": self.is_pinned,
            "access_count": self.access_count,
            "last_accessed_at": self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
