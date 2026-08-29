"""Source and evidence models."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Index, Float
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from database.connection import Base


class Source(Base):
    """Information source (web page, document, etc.)."""
    
    __tablename__ = "sources"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(PG_UUID(as_uuid=True), ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    url = Column(Text)
    title = Column(Text, nullable=False)
    source_metadata = Column(JSON().with_variant(JSONB, "postgresql"), default=dict)
    content_hash = Column(String(64), index=True)
    retrieved_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    job = relationship("ResearchJob", back_populates="sources")
    evidence = relationship("Evidence", back_populates="source", cascade="all, delete-orphan", lazy="dynamic")


class Evidence(Base):
    """Extracted evidence from a source."""
    
    __tablename__ = "evidence"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(PG_UUID(as_uuid=True), ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(PG_UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True)
    claim = Column(Text, nullable=False)
    supporting_text = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False, default=0.5)
    verification_status = Column(String(50), default="unverified")
    verification_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    job = relationship("ResearchJob", back_populates="evidence")
    source = relationship("Source", back_populates="evidence")
    
    __table_args__ = (
        Index("ix_evidence_job_verification", "job_id", "verification_status"),
    )