"""SQLAlchemy database models for AI Model Evaluations and Benchmark Results."""
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


class DBModelEvaluation(Base):
    """Historical benchmark evaluation run summary for a specific model."""

    __tablename__ = "model_evaluations"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    model_id = Column(String(100), nullable=False, index=True)
    provider_name = Column(String(50), nullable=False, index=True)
    benchmark_name = Column(String(100), nullable=False, default="research_core_eval_v1", index=True)
    total_samples = Column(Integer, nullable=False, default=0)
    passed_samples = Column(Integer, nullable=False, default=0)
    pass_rate = Column(Float, nullable=False, default=0.0)
    overall_score = Column(Float, nullable=False, default=0.0, index=True)
    mean_accuracy = Column(Float, nullable=False, default=0.0)
    mean_reasoning = Column(Float, nullable=False, default=0.0)
    mean_faithfulness = Column(Float, nullable=False, default=0.0)
    mean_citation_precision = Column(Float, nullable=False, default=0.0)
    mean_latency_ms = Column(Float, nullable=False, default=0.0)
    total_cost_usd = Column(Numeric(10, 6), nullable=False, default=0.0)
    category_scores = Column(JSONType, nullable=False, default=dict)
    triggered_by = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    # Relationships
    user = relationship("User", foreign_keys=[triggered_by])
    results = relationship("DBModelBenchmarkResult", back_populates="evaluation", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_model_evals_model_benchmark", "model_id", "benchmark_name"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "model_id": self.model_id,
            "provider_name": self.provider_name,
            "benchmark_name": self.benchmark_name,
            "total_samples": self.total_samples,
            "passed_samples": self.passed_samples,
            "pass_rate": round(self.pass_rate, 4),
            "overall_score": round(self.overall_score, 4),
            "mean_accuracy": round(self.mean_accuracy, 4),
            "mean_reasoning": round(self.mean_reasoning, 4),
            "mean_faithfulness": round(self.mean_faithfulness, 4),
            "mean_citation_precision": round(self.mean_citation_precision, 4),
            "mean_latency_ms": round(self.mean_latency_ms, 1),
            "total_cost_usd": float(self.total_cost_usd or 0.0),
            "category_scores": self.category_scores or {},
            "triggered_by": str(self.triggered_by) if self.triggered_by else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DBModelBenchmarkResult(Base):
    """Detailed score and assertions for a single benchmark test case within an evaluation run."""

    __tablename__ = "model_benchmark_results"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    evaluation_id = Column(GUID, ForeignKey("model_evaluations.id", ondelete="CASCADE"), nullable=False, index=True)
    sample_id = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    prompt = Column(Text, nullable=False)
    response_text = Column(Text, nullable=True)
    passed = Column(Boolean, nullable=False, default=False)
    score = Column(Float, nullable=False, default=0.0)
    metrics = Column(JSONType, nullable=False, default=dict)
    latency_ms = Column(Integer, nullable=False, default=0)
    prompt_tokens = Column(Integer, nullable=False, default=0)
    completion_tokens = Column(Integer, nullable=False, default=0)
    cost_usd = Column(Numeric(10, 6), nullable=False, default=0.0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    evaluation = relationship("DBModelEvaluation", back_populates="results")

    __table_args__ = (
        Index("ix_benchmark_res_eval_sample", "evaluation_id", "sample_id"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "evaluation_id": str(self.evaluation_id),
            "sample_id": self.sample_id,
            "category": self.category,
            "prompt": self.prompt,
            "response_text": self.response_text,
            "passed": self.passed,
            "score": round(self.score, 4),
            "metrics": self.metrics or {},
            "latency_ms": self.latency_ms,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "cost_usd": float(self.cost_usd or 0.0),
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
