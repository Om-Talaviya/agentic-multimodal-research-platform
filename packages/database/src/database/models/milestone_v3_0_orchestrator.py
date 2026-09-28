"""SQLAlchemy models for Phase 266: Autonomous Milestone v3.0 Planetary Multi-Omics Research Synthesis & Centennial Meta-Orchestrator Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MilestoneV30OrchestratorStudy(Base):
    """Study record for Centennial master meta-orchestrator across all 266 platform phases, synthesizing spatial multiome co-assays, antibody de-immunization, Perturb-seq epistasis, Cryo-EM MDFF, and minimal genomics.."""

    __tablename__ = "m30_meta_orchestrator_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="milestone-v3-0-orchestrator")
    centennial_planetary_orchestration_index = Column(Float, nullable=False, default=99.9)
    autonomous_pipeline_completion_rate_pct = Column(Float, nullable=False, default=100.0)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MilestoneV30OrchestratorItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("MilestoneV30OrchestratorMetricTrace", back_populates="study", cascade="all, delete-orphan")


class MilestoneV30OrchestratorItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "m30_meta_orchestrator_item_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("m30_meta_orchestrator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MilestoneV30OrchestratorStudy", back_populates="item_profiles")


class MilestoneV30OrchestratorMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "m30_meta_orchestrator_metric_traces"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("m30_meta_orchestrator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MilestoneV30OrchestratorStudy", back_populates="metric_traces")
