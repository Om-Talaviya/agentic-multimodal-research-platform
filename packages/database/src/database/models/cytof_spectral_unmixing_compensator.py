"""SQLAlchemy models for Phase 284: Autonomous In-Silico High-Dimensional CyTOF Spectral Unmixing & Mass Tag Cross-Talk Compensator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CytofSpectralUnmixingCompensatorStudy(Base):
    """Study record for Compensates for isotopic impurities, instrument mass tag spillover, and oxidation channels (M+16) in high-dimensional mass cytometry to purify single-cell ion signals.."""

    __tablename__ = "cytof_unmixing_comp_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="cytof-spectral-unmixing-compensator")
    signal_spillover_reduction_ratio_pct = Column(Float, nullable=False, default=98.6)
    single_cell_channel_cross_talk_residual = Column(Float, nullable=False, default=0.02)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CytofSpectralUnmixingCompensatorItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("CytofSpectralUnmixingCompensatorMetricTrace", back_populates="study", cascade="all, delete-orphan")


class CytofSpectralUnmixingCompensatorItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "cytof_unmixing_comp_item_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("cytof_unmixing_comp_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CytofSpectralUnmixingCompensatorStudy", back_populates="item_profiles")


class CytofSpectralUnmixingCompensatorMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "cytof_unmixing_comp_metric_traces"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("cytof_unmixing_comp_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CytofSpectralUnmixingCompensatorStudy", back_populates="metric_traces")
