"""SQLAlchemy models for Phase 518: Autonomous Milestone v4.8 Planetary Synthetic Biofoundry, Quantum Sensor Networks & Xenobiology OS Grand Meta-Orchestrator Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MilestoneV48MetaOrchestratorStudy(Base):
    """Study record for Autonomous Milestone v4.8 Planetary Synthetic Biofoundry, Quantum Sensor Networks & Xenobiology OS Grand Meta-Orchestrator Engine."""

    __tablename__ = "p518_milestone_v4_8_meta_orchestrator_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Integrated Milestone v4.8 Synthetic Biofoundry, MRFM Quantum Imaging, CAST Transposase & Living Bioelectronics Suite")
    analytical_modality = Column(String(100), nullable=False, default="planetary-v4-8-meta-orchestration")
    synthetic_biofoundry_orchestration_coherence = Column(Float, nullable=False, default=0.997)
    xenobiotic_chassis_cellular_compatibility_tau = Column(Float, nullable=False, default=0.993)
    cross_engine_federated_convergence_ratio = Column(Float, nullable=False, default=0.996)
    global_synthesis_confidence_score = Column(Float, nullable=False, default=0.999)
    confidence_score = Column(Float, nullable=False, default=0.999)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MilestoneV48MetaOrchestratorItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MilestoneV48MetaOrchestratorMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MilestoneV48MetaOrchestratorItemProfile(Base):
    """Detailed item profile for Autonomous Milestone v4.8 Planetary Synthetic Biofoundry, Quantum Sensor Networks & Xenobiology OS Grand Meta-Orchestrator Engine."""

    __tablename__ = "p518_milestone_v4_8_meta_orchestrator_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p518_milestone_v4_8_meta_orchestrator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MilestoneV48MetaOrchestratorStudy", back_populates="item_profiles")


class MilestoneV48MetaOrchestratorMetricTrace(Base):
    """Metric trace for Autonomous Milestone v4.8 Planetary Synthetic Biofoundry, Quantum Sensor Networks & Xenobiology OS Grand Meta-Orchestrator Engine."""

    __tablename__ = "p518_milestone_v4_8_meta_orchestrator_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p518_milestone_v4_8_meta_orchestrator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MilestoneV48MetaOrchestratorStudy", back_populates="metric_traces")
