"""SQLAlchemy models for Phase 497: Autonomous Milestone v4.7 Planetary Subcellular Nanomechanics, Quantum Biomolecular Electronics & Synthetic Organogenesis OS Grand Meta-Orchestrator Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MilestoneV47MetaOrchestratorStudy(Base):
    """Study record for Autonomous Milestone v4.7 Planetary Subcellular Nanomechanics, Quantum Biomolecular Electronics & Synthetic Organogenesis OS Grand Meta-Orchestrator Engine."""

    __tablename__ = "p497_milestone_v4_7_meta_orchestrator_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Integrated Milestone v4.7 Subcellular Nanomechanics, Quantum Magnetoreception & Synthetic Organogenesis Engine Suite")
    analytical_modality = Column(String(100), nullable=False, default="planetary-v4-7-meta-orchestration")
    subcellular_quantum_mechanics_coherence_index = Column(Float, nullable=False, default=0.996)
    organogenesis_morpho_kinetic_sync_tau = Column(Float, nullable=False, default=0.991)
    cross_engine_federated_convergence_ratio = Column(Float, nullable=False, default=0.994)
    global_synthesis_confidence_score = Column(Float, nullable=False, default=0.998)
    confidence_score = Column(Float, nullable=False, default=0.999)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MilestoneV47MetaOrchestratorItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MilestoneV47MetaOrchestratorMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MilestoneV47MetaOrchestratorItemProfile(Base):
    """Detailed item profile for Autonomous Milestone v4.7 Planetary Subcellular Nanomechanics, Quantum Biomolecular Electronics & Synthetic Organogenesis OS Grand Meta-Orchestrator Engine."""

    __tablename__ = "p497_milestone_v4_7_meta_orchestrator_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p497_milestone_v4_7_meta_orchestrator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MilestoneV47MetaOrchestratorStudy", back_populates="item_profiles")


class MilestoneV47MetaOrchestratorMetricTrace(Base):
    """Metric trace for Autonomous Milestone v4.7 Planetary Subcellular Nanomechanics, Quantum Biomolecular Electronics & Synthetic Organogenesis OS Grand Meta-Orchestrator Engine."""

    __tablename__ = "p497_milestone_v4_7_meta_orchestrator_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p497_milestone_v4_7_meta_orchestrator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MilestoneV47MetaOrchestratorStudy", back_populates="metric_traces")
