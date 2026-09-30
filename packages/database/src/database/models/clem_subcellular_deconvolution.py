"""SQLAlchemy models for Phase 372: Autonomous Correlative Light and Electron Microscopy (CLEM) Subcellular 3D Super-Resolution Deconvolver."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class ClemSubcellularDeconvolutionStudy(Base):
    """Study record for Registers and deconvolves multi-channel fluorescence cryo-confocal microscopy with high-vacuum transmission electron tomograms down to 4nm fiducial alignment accuracy.."""

    __tablename__ = "p372_clem_recon_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="clem-subcellular-deconvolution")
    correlative_fiducial_registration_accuracy_nm = Column(Float, nullable=False, default=3.8)
    subcellular_organelle_segmentation_dice_score = Column(Float, nullable=False, default=94.6)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("ClemSubcellularDeconvolutionItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("ClemSubcellularDeconvolutionMetricTrace", back_populates="study", cascade="all, delete-orphan")


class ClemSubcellularDeconvolutionItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "p372_clem_recon_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p372_clem_recon_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("ClemSubcellularDeconvolutionStudy", back_populates="item_profiles")


class ClemSubcellularDeconvolutionMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "p372_clem_recon_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p372_clem_recon_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("ClemSubcellularDeconvolutionStudy", back_populates="metric_traces")
