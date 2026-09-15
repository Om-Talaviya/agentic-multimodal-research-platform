"""Report model."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class Report(Base):
    """Generated research report."""
    
    __tablename__ = "reports"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    job_id = Column(GUID(), ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(Text, nullable=False)
    executive_summary = Column(Text)
    methodology = Column(Text)
    findings = Column(JSON().with_variant(JSONB, "postgresql"), default=list)
    evidence_ids = Column(JSON().with_variant(JSONB, "postgresql"), default=list)
    source_ids = Column(JSON().with_variant(JSONB, "postgresql"), default=list)
    contradictions = Column(JSON().with_variant(JSONB, "postgresql"), default=list)
    confidence_score = Column(Float, nullable=False, default=0.85)
    conclusions = Column(JSON().with_variant(JSONB, "postgresql"), default=list)
    limitations = Column(JSON().with_variant(JSONB, "postgresql"), default=list)
    generated_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    
    # Relationships
    job = relationship("ResearchJob", back_populates="reports")
