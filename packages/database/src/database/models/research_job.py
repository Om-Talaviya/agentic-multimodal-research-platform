"""Research job and task models."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Integer, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class ResearchJob(Base):
    """Research job - top-level research request."""
    
    __tablename__ = "research_jobs"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    question = Column(Text, nullable=False)
    objective = Column(Text, nullable=False)
    domain = Column(String(255))
    scope = Column(Text)
    constraints = Column(JSON().with_variant(JSONB, "postgresql"), default=list)
    expected_output = Column(String(100), default="report")
    status = Column(String(50), nullable=False, default="pending", index=True)
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    tasks = relationship("ResearchTask", back_populates="job", cascade="all, delete-orphan", lazy="dynamic")
    sources = relationship("Source", back_populates="job", cascade="all, delete-orphan", lazy="dynamic")
    evidence = relationship("Evidence", back_populates="job", cascade="all, delete-orphan", lazy="dynamic")
    documents = relationship("Document", back_populates="job", cascade="all, delete-orphan", lazy="dynamic")
    reports = relationship("Report", back_populates="job", cascade="all, delete-orphan", lazy="dynamic")
    agent_runs = relationship("AgentRun", back_populates="job", cascade="all, delete-orphan", lazy="dynamic")
    
    __table_args__ = (
        Index("ix_research_jobs_created_at", "created_at"),
        Index("ix_research_jobs_status_created", "status", "created_at"),
    )


class ResearchTask(Base):
    """Individual task within a research job."""
    
    __tablename__ = "research_tasks"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(PG_UUID(as_uuid=True), ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(100), nullable=False)
    objective = Column(Text, nullable=False)
    context = Column(JSON().with_variant(JSONB, "postgresql"), default=dict)
    agent = Column(String(100), nullable=False)
    inputs = Column(JSON().with_variant(JSONB, "postgresql"), default=dict)
    depends_on = Column(JSON().with_variant(JSONB, "postgresql"), default=list)
    priority = Column(Integer, default=1)
    status = Column(String(50), nullable=False, default="pending", index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    result = Column(JSON().with_variant(JSONB, "postgresql"))
    
    # Relationships
    job = relationship("ResearchJob", back_populates="tasks")
    
    __table_args__ = (
        Index("ix_research_tasks_job_status", "job_id", "status"),
    )
