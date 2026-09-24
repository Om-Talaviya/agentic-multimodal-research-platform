"""Phase 154: Centennial Bio-System Synthesis & Milestone v1.8 Orchestration Models."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBMilestoneV18Orchestration(Base):
    """Milestone v1.8 Multi-Domain Cross-Scale Synthesis Pipeline."""

    __tablename__ = "milestone_v1_8_orchestrations"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    orchestration_name = Column(String(255), nullable=False)
    milestone_version = Column(String(32), default="v1.8")
    total_phases_integrated = Column(Integer, default=154, nullable=False)
    cross_domain_pipeline_status = Column(String(64), default="SYNCHRONIZED")
    orchestration_confidence_score = Column(Float, default=0.985)
    global_system_entropy = Column(Float, default=0.018)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    workflow_nodes = relationship("DBCrossDomainWorkflowNode", back_populates="orchestration", cascade="all, delete-orphan")
    synthesis_reports = relationship("DBSynthesisExecutiveReport", back_populates="orchestration", cascade="all, delete-orphan")


class DBCrossDomainWorkflowNode(Base):
    """Execution step connecting multi-modal biophysical and AI phases."""

    __tablename__ = "cross_domain_workflow_nodes"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    orchestration_id = Column(GUID(), ForeignKey("milestone_v1_8_orchestrations.id", ondelete="CASCADE"), nullable=False)
    node_name = Column(String(120), nullable=False)
    domain_category = Column(String(120), nullable=False)
    phase_reference = Column(String(64), nullable=False)
    execution_latency_ms = Column(Float, nullable=False)
    node_fidelity_score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    orchestration = relationship("DBMilestoneV18Orchestration", back_populates="workflow_nodes")


class DBSynthesisExecutiveReport(Base):
    """Executive synthesis document summarizing cross-scale discoveries."""

    __tablename__ = "synthesis_executive_reports"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    orchestration_id = Column(GUID(), ForeignKey("milestone_v1_8_orchestrations.id", ondelete="CASCADE"), nullable=False)
    report_title = Column(String(255), nullable=False)
    executive_summary = Column(Text, nullable=False)
    primary_breakthrough = Column(String(255), nullable=False)
    recommended_clinical_translation = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    orchestration = relationship("DBMilestoneV18Orchestration", back_populates="synthesis_reports")
