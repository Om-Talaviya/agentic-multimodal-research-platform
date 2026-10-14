"""SQLAlchemy models for Phase 492: Autonomous Multi-Organ Microphysiological Human-on-a-Chip Endocrine-Metabolic Feedback Loop."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class HumanOnChipEndocrineFeedbackStudy(Base):
    """Study record for Autonomous Multi-Organ Microphysiological Human-on-a-Chip Endocrine-Metabolic Feedback Loop."""

    __tablename__ = "p492_human_on_chip_endocrine_feedback_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="4-Organ Interconnected Microfluidic Platform (Liver Spheroids, Islet Organoids, Adipose, Skeletal Muscle)")
    analytical_modality = Column(String(100), nullable=False, default="human-on-chip-endocrine-loop")
    glucose_stimulated_insulin_secretion_gsis_index = Column(Float, nullable=False, default=3.85)
    hepatic_glucose_uptake_rate_uM_per_hr = Column(Float, nullable=False, default=42.0)
    inter_organ_circulatory_perfusion_flow_uL_per_min = Column(Float, nullable=False, default=5.0)
    homeostatic_endocrine_feedback_sync_tau = Column(Float, nullable=False, default=0.985)
    confidence_score = Column(Float, nullable=False, default=0.995)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("HumanOnChipEndocrineFeedbackItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("HumanOnChipEndocrineFeedbackMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class HumanOnChipEndocrineFeedbackItemProfile(Base):
    """Detailed item profile for Autonomous Multi-Organ Microphysiological Human-on-a-Chip Endocrine-Metabolic Feedback Loop."""

    __tablename__ = "p492_human_on_chip_endocrine_feedback_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p492_human_on_chip_endocrine_feedback_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("HumanOnChipEndocrineFeedbackStudy", back_populates="item_profiles")


class HumanOnChipEndocrineFeedbackMetricTrace(Base):
    """Metric trace for Autonomous Multi-Organ Microphysiological Human-on-a-Chip Endocrine-Metabolic Feedback Loop."""

    __tablename__ = "p492_human_on_chip_endocrine_feedback_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p492_human_on_chip_endocrine_feedback_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("HumanOnChipEndocrineFeedbackStudy", back_populates="metric_traces")
