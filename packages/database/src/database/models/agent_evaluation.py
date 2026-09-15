"""SQLAlchemy database models for Autonomous Agent Evaluations and Step Telemetry."""
from datetime import UTC, datetime
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID, JSONType


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBAgentEvaluation(Base):
    """Evaluation scorecard for an agent run or research job."""

    __tablename__ = "agent_evaluations"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    job_id = Column(GUID, ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=True, index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    total_steps = Column(Integer, nullable=False, default=0)
    successful_steps = Column(Integer, nullable=False, default=0)
    failed_steps = Column(Integer, nullable=False, default=0)
    plan_precision = Column(Float, nullable=False, default=0.0)
    tool_accuracy = Column(Float, nullable=False, default=0.0)
    evidence_coverage = Column(Float, nullable=False, default=0.0)
    hallucination_rate = Column(Float, nullable=False, default=0.0)
    synthesis_fidelity = Column(Float, nullable=False, default=0.0)
    overall_score = Column(Float, nullable=False, default=0.0, index=True)
    execution_time_ms = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)
    estimated_cost_usd = Column(Numeric(10, 6), nullable=False, default=0.0)
    findings_audit = Column(JSONType, nullable=False, default=dict)
    evaluated_by = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    # Relationships
    job = relationship("ResearchJob", foreign_keys=[job_id])
    user = relationship("User", foreign_keys=[evaluated_by])
    steps = relationship("DBAgentStepMetric", back_populates="evaluation", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_agent_evals_agent_job", "agent_name", "job_id"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "job_id": str(self.job_id) if self.job_id else None,
            "agent_name": self.agent_name,
            "total_steps": self.total_steps,
            "successful_steps": self.successful_steps,
            "failed_steps": self.failed_steps,
            "plan_precision": self.plan_precision,
            "tool_accuracy": self.tool_accuracy,
            "evidence_coverage": self.evidence_coverage,
            "hallucination_rate": self.hallucination_rate,
            "synthesis_fidelity": self.synthesis_fidelity,
            "overall_score": self.overall_score,
            "execution_time_ms": self.execution_time_ms,
            "total_tokens": self.total_tokens,
            "estimated_cost_usd": float(self.estimated_cost_usd),
            "findings_audit": self.findings_audit or {},
            "evaluated_by": str(self.evaluated_by) if self.evaluated_by else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DBAgentStepMetric(Base):
    """Detailed step-level telemetry recorded during agent execution."""

    __tablename__ = "agent_step_metrics"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    evaluation_id = Column(GUID, ForeignKey("agent_evaluations.id", ondelete="CASCADE"), nullable=False, index=True)
    step_index = Column(Integer, nullable=False)
    agent_type = Column(String(50), nullable=False)
    action_type = Column(String(50), nullable=False)
    tool_name = Column(String(100), nullable=True)
    tool_args = Column(JSONType, nullable=False, default=dict)
    tool_output_length = Column(Integer, nullable=False, default=0)
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(Text, nullable=True)
    latency_ms = Column(Integer, nullable=False, default=0)
    tokens_consumed = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    evaluation = relationship("DBAgentEvaluation", back_populates="steps")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "evaluation_id": str(self.evaluation_id),
            "step_index": self.step_index,
            "agent_type": self.agent_type,
            "action_type": self.action_type,
            "tool_name": self.tool_name,
            "tool_args": self.tool_args or {},
            "tool_output_length": self.tool_output_length,
            "success": self.success,
            "error_message": self.error_message,
            "latency_ms": self.latency_ms,
            "tokens_consumed": self.tokens_consumed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
