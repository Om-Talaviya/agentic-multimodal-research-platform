"""SQLAlchemy models for RAGAS Groundedness Evaluation & Adversarial Red-Teaming Guardrails (Phase 51)."""
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
from database.models.memory import GUID, JSONType


class DBRagasEvaluationSuite(Base):
    """Evaluation benchmark suite measuring RAG faithfulness, groundedness, and security."""

    __tablename__ = "ragas_evaluation_suites"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_pipeline_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    total_samples: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_faithfulness: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_answer_relevancy: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_context_precision: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_context_recall: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_groundedness: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    red_team_defense_rate: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="COMPLETED")
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSONType, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    samples: Mapped[List["DBRagasSampleMetric"]] = relationship(
        "DBRagasSampleMetric", back_populates="suite", cascade="all, delete-orphan"
    )
    probes: Mapped[List["DBAdversarialRedTeamProbe"]] = relationship(
        "DBAdversarialRedTeamProbe", back_populates="suite", cascade="all, delete-orphan"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "target_pipeline_id": self.target_pipeline_id,
            "total_samples": self.total_samples,
            "avg_faithfulness": self.avg_faithfulness,
            "avg_answer_relevancy": self.avg_answer_relevancy,
            "avg_context_precision": self.avg_context_precision,
            "avg_context_recall": self.avg_context_recall,
            "avg_groundedness": self.avg_groundedness,
            "red_team_defense_rate": self.red_team_defense_rate,
            "status": self.status,
            "metadata_json": self.metadata_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DBRagasSampleMetric(Base):
    """Per-query sample evaluation metrics."""

    __tablename__ = "ragas_sample_metrics"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    suite_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("ragas_evaluation_suites.id", ondelete="CASCADE"), nullable=False, index=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    generated_answer: Mapped[str] = mapped_column(Text, nullable=False)
    ground_truth: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retrieved_contexts: Mapped[List[str]] = mapped_column(JSONType, nullable=False, default=list)
    faithfulness_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    answer_relevancy_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    context_precision_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    context_recall_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    groundedness_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    hallucination_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    suite: Mapped["DBRagasEvaluationSuite"] = relationship("DBRagasEvaluationSuite", back_populates="samples")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "suite_id": str(self.suite_id),
            "query": self.query,
            "generated_answer": self.generated_answer,
            "ground_truth": self.ground_truth,
            "retrieved_contexts": self.retrieved_contexts,
            "faithfulness_score": self.faithfulness_score,
            "answer_relevancy_score": self.answer_relevancy_score,
            "context_precision_score": self.context_precision_score,
            "context_recall_score": self.context_recall_score,
            "groundedness_score": self.groundedness_score,
            "hallucination_flag": self.hallucination_flag,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DBAdversarialRedTeamProbe(Base):
    """Adversarial security attack probe and guardrail response."""

    __tablename__ = "adversarial_red_team_probes"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    suite_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("ragas_evaluation_suites.id", ondelete="CASCADE"), nullable=False, index=True)
    attack_category: Mapped[str] = mapped_column(String(100), nullable=False)  # PROMPT_INJECTION, JAILBREAK, DATA_EXFILTRATION, SSRF
    prompt_payload: Mapped[str] = mapped_column(Text, nullable=False)
    guardrail_verdict: Mapped[str] = mapped_column(String(50), nullable=False, default="BLOCKED")  # BLOCKED, FLAGGED, PASSED
    mitigation_applied: Mapped[str] = mapped_column(String(255), nullable=False, default="Input Sanitizer Filter & SSRF Firewall")
    is_defense_successful: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=12.5)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    suite: Mapped["DBRagasEvaluationSuite"] = relationship("DBRagasEvaluationSuite", back_populates="probes")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "suite_id": str(self.suite_id),
            "attack_category": self.attack_category,
            "prompt_payload": self.prompt_payload,
            "guardrail_verdict": self.guardrail_verdict,
            "mitigation_applied": self.mitigation_applied,
            "is_defense_successful": self.is_defense_successful,
            "latency_ms": self.latency_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
