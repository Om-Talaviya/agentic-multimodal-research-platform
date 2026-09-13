"""Agent run and model call models."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Integer, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class AgentRun(Base):
    """Agent execution trace for observability."""
    
    __tablename__ = "agent_runs"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(PG_UUID(as_uuid=True), ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(PG_UUID(as_uuid=True), ForeignKey("research_tasks.id", ondelete="SET NULL"), index=True)
    agent_name = Column(String(100), nullable=False)
    request_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at = Column(DateTime(timezone=True))
    success = Column(Boolean)
    input = Column(JSON().with_variant(JSONB, "postgresql"))
    output = Column(JSON().with_variant(JSONB, "postgresql"))
    tool_calls = Column(JSON().with_variant(JSONB, "postgresql"), default=list)
    model_calls = Column(JSON().with_variant(JSONB, "postgresql"), default=list)
    errors = Column(JSON().with_variant(JSONB, "postgresql"), default=list)
    duration_ms = Column(Integer)
    
    # Relationships
    job = relationship("ResearchJob", back_populates="agent_runs")
    model_calls_rel = relationship("ModelCall", back_populates="agent_run", cascade="all, delete-orphan", lazy="dynamic")
    
    __table_args__ = (
        Index("ix_agent_runs_job_started", "job_id", "started_at"),
        Index("ix_agent_runs_agent", "agent_name"),
    )


class ModelCall(Base):
    """Individual model API call log."""
    
    __tablename__ = "model_calls"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_run_id = Column(PG_UUID(as_uuid=True), ForeignKey("agent_runs.id", ondelete="CASCADE"), index=True)
    provider = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    request_type = Column(String(50), nullable=False)  # complete, stream, embed, vision, rerank
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    total_tokens = Column(Integer)
    latency_ms = Column(Integer)
    success = Column(Boolean)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    
    # Relationships
    agent_run = relationship("AgentRun", back_populates="model_calls_rel")
    
    __table_args__ = (
        Index("ix_model_calls_provider_model", "provider", "model"),
        Index("ix_model_calls_created", "created_at"),
    )
