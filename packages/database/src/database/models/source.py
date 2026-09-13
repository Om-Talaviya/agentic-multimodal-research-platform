"""Source and evidence models."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Index, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class Source(Base):
    """Information source (web page, document, etc.)."""
    
    __tablename__ = "sources"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    job_id = Column(GUID(), ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    url = Column(Text)
    title = Column(Text, nullable=False)
    source_metadata = Column(JSON().with_variant(JSONB, "postgresql"), default=dict)
    content_hash = Column(String(64), index=True)
    retrieved_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    
    # Relationships
    job = relationship("ResearchJob", back_populates="sources")
    evidence = relationship("Evidence", back_populates="source", cascade="all, delete-orphan", lazy="dynamic")


class Evidence(Base):
    """Extracted evidence from a source."""
    
    __tablename__ = "evidence"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    job_id = Column(GUID(), ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(GUID(), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True)
    claim = Column(Text, nullable=False)
    supporting_text = Column(Text, nullable=False, default="")
    confidence = Column(Float, nullable=False, default=0.5)
    source_reliability = Column(Float, nullable=False, default=1.0)
    verification_status = Column(String(50), default="unverified")
    verification_notes = Column(Text)
    citation_coordinates = Column(JSON().with_variant(JSONB, "postgresql"), default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    
    # Relationships
    job = relationship("ResearchJob", back_populates="evidence")
    source = relationship("Source", back_populates="evidence")
    
    __table_args__ = (
        Index("ix_evidence_job_verification", "job_id", "verification_status"),
    )
