"""Database models for Research Automation, Scheduled Sweeps, and Alerting."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON
from database.connection import Base
from database.models.memory import GUID


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DBScheduledResearch(Base):
    """Represents a recurring scheduled research sweep job."""

    __tablename__ = "scheduled_research"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    workspace_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(), ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    query_topic: Mapped[str] = mapped_column(Text, nullable=False)
    cron_expression: Mapped[str] = mapped_column(String(100), nullable=False, default="0 9 * * 1-5")
    routing_profile: Mapped[str] = mapped_column(String(50), nullable=False, default="balanced")
    source_types: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=lambda: ["web", "academic", "knowledge_vault"],
        nullable=False,
    )
    novelty_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.30)
    confidence_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.85)
    contradiction_alert: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    webhook_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    email_notifications: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=list, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active", index=True
    )  # 'active', 'paused', 'completed', 'failed'
    total_sweeps_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_findings_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationships
    sweeps: Mapped[List["DBResearchSweepResult"]] = relationship(
        "DBResearchSweepResult",
        back_populates="schedule",
        cascade="all, delete-orphan",
        order_by="desc(DBResearchSweepResult.executed_at)",
    )
    alerts: Mapped[List["DBAutomationAlert"]] = relationship(
        "DBAutomationAlert",
        back_populates="schedule",
        cascade="all, delete-orphan",
        order_by="desc(DBAutomationAlert.created_at)",
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "workspace_id": str(self.workspace_id) if self.workspace_id else None,
            "title": self.title,
            "query_topic": self.query_topic,
            "cron_expression": self.cron_expression,
            "routing_profile": self.routing_profile,
            "source_types": self.source_types or [],
            "novelty_threshold": self.novelty_threshold,
            "confidence_threshold": self.confidence_threshold,
            "contradiction_alert": self.contradiction_alert,
            "webhook_url": self.webhook_url,
            "email_notifications": self.email_notifications or [],
            "status": self.status,
            "total_sweeps_count": self.total_sweeps_count,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "last_findings_summary": self.last_findings_summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DBResearchSweepResult(Base):
    """Records the execution outcome and diff analysis of a research sweep run."""

    __tablename__ = "research_sweep_results"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    schedule_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("scheduled_research.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(), ForeignKey("research_jobs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="completed", index=True
    )  # 'completed', 'no_novel_findings', 'alert_dispatched', 'failed'
    findings_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    novel_claims_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    novelty_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    novel_claims: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=list, nullable=False
    )
    contradictions_found: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=list, nullable=False
    )
    alert_dispatched: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    execution_duration_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False, index=True
    )

    # Relationships
    schedule: Mapped["DBScheduledResearch"] = relationship(
        "DBScheduledResearch", back_populates="sweeps"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "schedule_id": str(self.schedule_id),
            "job_id": str(self.job_id) if self.job_id else None,
            "status": self.status,
            "findings_count": self.findings_count,
            "novel_claims_count": self.novel_claims_count,
            "novelty_score": round(self.novelty_score, 4),
            "novel_claims": self.novel_claims or [],
            "contradictions_found": self.contradictions_found or [],
            "alert_dispatched": self.alert_dispatched,
            "execution_duration_ms": round(self.execution_duration_ms, 2),
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
        }


class DBAutomationAlert(Base):
    """Dispatched alert notification triggered by novelty or contradictions in research sweeps."""

    __tablename__ = "automation_alerts"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    schedule_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("scheduled_research.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sweep_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(), ForeignKey("research_sweep_results.id", ondelete="SET NULL"), nullable=True, index=True
    )
    job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(), ForeignKey("research_jobs.id", ondelete="SET NULL"), nullable=True
    )
    workspace_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(), ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(
        String(50), nullable=False, default="info", index=True
    )  # 'info', 'warning', 'critical'
    channel: Mapped[str] = mapped_column(
        String(50), nullable=False, default="in_app"
    )  # 'in_app', 'webhook', 'email'
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=dict, nullable=False
    )
    is_acknowledged: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False, index=True
    )

    # Relationships
    schedule: Mapped["DBScheduledResearch"] = relationship(
        "DBScheduledResearch", back_populates="alerts"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "schedule_id": str(self.schedule_id),
            "sweep_id": str(self.sweep_id) if self.sweep_id else None,
            "job_id": str(self.job_id) if self.job_id else None,
            "workspace_id": str(self.workspace_id) if self.workspace_id else None,
            "title": self.title,
            "severity": self.severity,
            "channel": self.channel,
            "message": self.message,
            "payload": self.payload or {},
            "is_acknowledged": self.is_acknowledged,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
