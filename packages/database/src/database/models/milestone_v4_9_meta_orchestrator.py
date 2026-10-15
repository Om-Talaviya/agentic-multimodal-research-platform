"""SQLAlchemy models for Phase 539: Autonomous Milestone v4.9 Planetary Cryo-Architecture, Non-Equilibrium Active Matter & Neuromorphic Quantum Bio-Computing OS Grand Meta-Orchestrator Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MilestoneV49MetaOrchestratorStudy(Base):
    """Study record for Autonomous Milestone v4.9 Planetary Cryo-Architecture, Non-Equilibrium Active Matter & Neuromorphic Quantum Bio-Computing OS Grand Meta-Orchestrator Engine."""

    __tablename__ = "p539_milestone_v4_9_meta_orchestrator_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Global Milestone v4.9 Distributed Multi-Agent DAG Across Phases 519-539")
    analytical_modality = Column(String(100), nullable=False, default="milestone-v4-9-planetary-orchestration")
    cross_phase_dag_convergence_tau = Column(Float, nullable=False, default=0.998)
    multi_agent_consensus_fidelity_pct = Column(Float, nullable=False, default=99.5)
    sub_angstrom_simulation_accuracy_score = Column(Float, nullable=False, default=0.994)
    closed_loop_autonomous_cycle_time_s = Column(Float, nullable=False, default=14.2)
    confidence_score = Column(Float, nullable=False, default=0.999)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MilestoneV49MetaOrchestratorItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MilestoneV49MetaOrchestratorMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MilestoneV49MetaOrchestratorItemProfile(Base):
    """Detailed item profile for Autonomous Milestone v4.9 Planetary Cryo-Architecture, Non-Equilibrium Active Matter & Neuromorphic Quantum Bio-Computing OS Grand Meta-Orchestrator Engine."""

    __tablename__ = "p539_milestone_v4_9_meta_orchestrator_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p539_milestone_v4_9_meta_orchestrator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MilestoneV49MetaOrchestratorStudy", back_populates="item_profiles")


class MilestoneV49MetaOrchestratorMetricTrace(Base):
    """Metric trace for Autonomous Milestone v4.9 Planetary Cryo-Architecture, Non-Equilibrium Active Matter & Neuromorphic Quantum Bio-Computing OS Grand Meta-Orchestrator Engine."""

    __tablename__ = "p539_milestone_v4_9_meta_orchestrator_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p539_milestone_v4_9_meta_orchestrator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MilestoneV49MetaOrchestratorStudy", back_populates="metric_traces")
