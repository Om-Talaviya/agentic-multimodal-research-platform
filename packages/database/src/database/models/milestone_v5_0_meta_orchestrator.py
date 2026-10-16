"""SQLAlchemy models for Phase 560: Autonomous Milestone v5.0 Planetary Multi-Scale Biodynamics, Quantum Bio-Spintronics & Cellular Reprogramming OS Grand Meta-Orchestrator Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MilestoneV50MetaOrchestratorStudy(Base):
    """Study record for Autonomous Milestone v5.0 Planetary Multi-Scale Biodynamics, Quantum Bio-Spintronics & Cellular Reprogramming OS Grand Meta-Orchestrator Engine."""

    __tablename__ = "p560_milestone_v5_0_meta_orchestrator_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Full Planetary Biodynamics, Quantum Spin Sensing, Direct RNA, Neuromorphic Optogenetics & Cellular Reprogramming Unified Grid")
    analytical_modality = Column(String(100), nullable=False, default="planetary-v5-0-meta-orchestration")
    multi_scale_cross_engine_coupling_efficiency_pct = Column(Float, nullable=False, default=99.8)
    quantum_spintronic_fidelity_index = Column(Float, nullable=False, default=0.994)
    subcellular_reprogramming_convergence_rate = Column(Float, nullable=False, default=0.985)
    total_orchestrated_milestone_phases = Column(Float, nullable=False, default=560.0)
    confidence_score = Column(Float, nullable=False, default=0.999)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MilestoneV50MetaOrchestratorItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MilestoneV50MetaOrchestratorMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MilestoneV50MetaOrchestratorItemProfile(Base):
    """Detailed item profile for Autonomous Milestone v5.0 Planetary Multi-Scale Biodynamics, Quantum Bio-Spintronics & Cellular Reprogramming OS Grand Meta-Orchestrator Engine."""

    __tablename__ = "p560_milestone_v5_0_meta_orchestrator_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p560_milestone_v5_0_meta_orchestrator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MilestoneV50MetaOrchestratorStudy", back_populates="item_profiles")


class MilestoneV50MetaOrchestratorMetricTrace(Base):
    """Metric trace for Autonomous Milestone v5.0 Planetary Multi-Scale Biodynamics, Quantum Bio-Spintronics & Cellular Reprogramming OS Grand Meta-Orchestrator Engine."""

    __tablename__ = "p560_milestone_v5_0_meta_orchestrator_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p560_milestone_v5_0_meta_orchestrator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MilestoneV50MetaOrchestratorStudy", back_populates="metric_traces")
