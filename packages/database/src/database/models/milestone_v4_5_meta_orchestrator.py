"""SQLAlchemy models for Phase 455: Autonomous Milestone v4.5 Planetary Nanoscale Biomachines, Quantum Biology & Synthetic Consortia Grand Meta-Orchestrator Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MilestoneV45MetaOrchestratorStudy(Base):
    """Study record for Autonomous Milestone v4.5 Planetary Nanoscale Biomachines, Quantum Biology & Synthetic Consortia Grand Meta-Orchestrator Engine."""

    __tablename__ = "p455_milestone_v4_5_meta_orchestrator_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Unified Cross-Domain Multimodal Biosphere Supercomputing Matrix across 21 Research Studios")
    analytical_modality = Column(String(100), nullable=False, default="milestone-v4-5-planetary-synthesis")
    cross_modality_synthesis_entropy = Column(Float, nullable=False, default=0.125)
    quantum_biomolecular_convergence_index = Column(Float, nullable=False, default=0.994)
    consortium_supercomputing_orchestration_score = Column(Float, nullable=False, default=0.988)
    grand_unification_fidelity_tau = Column(Float, nullable=False, default=0.992)
    confidence_score = Column(Float, nullable=False, default=0.999)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MilestoneV45MetaOrchestratorItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MilestoneV45MetaOrchestratorMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MilestoneV45MetaOrchestratorItemProfile(Base):
    """Detailed item profile for Autonomous Milestone v4.5 Planetary Nanoscale Biomachines, Quantum Biology & Synthetic Consortia Grand Meta-Orchestrator Engine."""

    __tablename__ = "p455_milestone_v4_5_meta_orchestrator_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p455_milestone_v4_5_meta_orchestrator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MilestoneV45MetaOrchestratorStudy", back_populates="item_profiles")


class MilestoneV45MetaOrchestratorMetricTrace(Base):
    """Metric trace for Autonomous Milestone v4.5 Planetary Nanoscale Biomachines, Quantum Biology & Synthetic Consortia Grand Meta-Orchestrator Engine."""

    __tablename__ = "p455_milestone_v4_5_meta_orchestrator_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p455_milestone_v4_5_meta_orchestrator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MilestoneV45MetaOrchestratorStudy", back_populates="metric_traces")
