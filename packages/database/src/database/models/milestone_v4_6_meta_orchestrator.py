"""SQLAlchemy models for Phase 476: Autonomous Milestone v4.6 Planetary Synthetic Morphogenesis, Biohybrid Cybernetics & Multicellular OS Grand Meta-Orchestrator Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MilestoneV46MetaOrchestratorStudy(Base):
    """Study record for Autonomous Milestone v4.6 Planetary Synthetic Morphogenesis, Biohybrid Cybernetics & Multicellular OS Grand Meta-Orchestrator Engine."""

    __tablename__ = "p476_milestone_v4_6_meta_orchestrator_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Integrated Milestone v4.6 Multi-Tissue Synthetic Morphogenesis, Biohybrid Soft Cybernetics & Multicellular Engine Suite")
    analytical_modality = Column(String(100), nullable=False, default="planetary-v4-6-meta-orchestration")
    multicellular_morphogenesis_coherence_index = Column(Float, nullable=False, default=0.995)
    biohybrid_actuation_cybernetic_sync_tau = Column(Float, nullable=False, default=0.988)
    cross_engine_federated_convergence_ratio = Column(Float, nullable=False, default=0.992)
    global_synthesis_confidence_score = Column(Float, nullable=False, default=0.997)
    confidence_score = Column(Float, nullable=False, default=0.998)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MilestoneV46MetaOrchestratorItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MilestoneV46MetaOrchestratorMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MilestoneV46MetaOrchestratorItemProfile(Base):
    """Detailed item profile for Autonomous Milestone v4.6 Planetary Synthetic Morphogenesis, Biohybrid Cybernetics & Multicellular OS Grand Meta-Orchestrator Engine."""

    __tablename__ = "p476_milestone_v4_6_meta_orchestrator_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p476_milestone_v4_6_meta_orchestrator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MilestoneV46MetaOrchestratorStudy", back_populates="item_profiles")


class MilestoneV46MetaOrchestratorMetricTrace(Base):
    """Metric trace for Autonomous Milestone v4.6 Planetary Synthetic Morphogenesis, Biohybrid Cybernetics & Multicellular OS Grand Meta-Orchestrator Engine."""

    __tablename__ = "p476_milestone_v4_6_meta_orchestrator_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p476_milestone_v4_6_meta_orchestrator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MilestoneV46MetaOrchestratorStudy", back_populates="metric_traces")
