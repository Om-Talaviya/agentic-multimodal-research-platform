"""SQLAlchemy models for Phase 367: Autonomous High-Resolution Optical Projection Tomography (OPT) Whole-Organ Cleared Tissue Reconstructor."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class OptWholeOrganTomographyStudy(Base):
    """Study record for Performs filtered back-projection (FBP) radon transform inversion on 360-degree optical projections of solvent-cleared (CUBIC/iDISCO) intact human organs with isotropic 5um cellular resolution.."""

    __tablename__ = "p367_opt_tomo_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="opt-whole-organ-tomography")
    isotropic_spatial_voxel_resolution_microns = Column(Float, nullable=False, default=5.0)
    volumetric_reconstruction_ssim_index = Column(Float, nullable=False, default=0.965)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("OptWholeOrganTomographyItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("OptWholeOrganTomographyMetricTrace", back_populates="study", cascade="all, delete-orphan")


class OptWholeOrganTomographyItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "p367_opt_tomo_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p367_opt_tomo_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OptWholeOrganTomographyStudy", back_populates="item_profiles")


class OptWholeOrganTomographyMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "p367_opt_tomo_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p367_opt_tomo_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OptWholeOrganTomographyStudy", back_populates="metric_traces")
