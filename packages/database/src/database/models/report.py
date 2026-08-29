"""Report model."""

import uuid
from datetime import datetime
from sqlalchemy import Column, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from database.connection import Base


class Report(Base):
    """Generated research report."""
    
    __tablename__ = "reports"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(PG_UUID(as_uuid=True), ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(Text, nullable=False)
    executive_summary = Column(Text)
    methodology = Column(Text)
    findings = Column(JSON().with_variant(JSONB, "postgresql"), default=list)
    evidence_ids = Column(JSON().with_variant(JSONB, "postgresql"), default=list)
    source_ids = Column(JSON().with_variant(JSONB, "postgresql"), default=list)
    conclusions = Column(JSON().with_variant(JSONB, "postgresql"), default=list)
    limitations = Column(JSON().with_variant(JSONB, "postgresql"), default=list)
    generated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    job = relationship("ResearchJob", back_populates="reports")