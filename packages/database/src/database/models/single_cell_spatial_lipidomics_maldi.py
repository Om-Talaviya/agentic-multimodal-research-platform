"""SQLAlchemy models for Phase 532: Autonomous High-Mass-Resolution MALDI MSI Single-Cell Spatial Phospholipid Fingerprinter."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SingleCellSpatialLipidomicsMaldiStudy(Base):
    """Study record for Autonomous High-Mass-Resolution MALDI MSI Single-Cell Spatial Phospholipid Fingerprinter."""

    __tablename__ = "p532_single_cell_spatial_lipidomics_maldi_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="High-Precision Cryo-Sectioned Mouse Brain Cortical Layer with 5um Sub-Cellular Laser Spot")
    analytical_modality = Column(String(100), nullable=False, default="single-cell-maldi-lipidomics")
    phospholipid_species_resolved_count = Column(Float, nullable=False, default=385.0)
    spatial_laser_ablation_pitch_um = Column(Float, nullable=False, default=5.0)
    mass_resolving_power_fwhm_at_m_z_800 = Column(Float, nullable=False, default=140000.0)
    cell_type_lipidomic_silhouette_score = Column(Float, nullable=False, default=0.89)
    confidence_score = Column(Float, nullable=False, default=0.995)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SingleCellSpatialLipidomicsMaldiItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SingleCellSpatialLipidomicsMaldiMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SingleCellSpatialLipidomicsMaldiItemProfile(Base):
    """Detailed item profile for Autonomous High-Mass-Resolution MALDI MSI Single-Cell Spatial Phospholipid Fingerprinter."""

    __tablename__ = "p532_single_cell_spatial_lipidomics_maldi_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p532_single_cell_spatial_lipidomics_maldi_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SingleCellSpatialLipidomicsMaldiStudy", back_populates="item_profiles")


class SingleCellSpatialLipidomicsMaldiMetricTrace(Base):
    """Metric trace for Autonomous High-Mass-Resolution MALDI MSI Single-Cell Spatial Phospholipid Fingerprinter."""

    __tablename__ = "p532_single_cell_spatial_lipidomics_maldi_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p532_single_cell_spatial_lipidomics_maldi_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SingleCellSpatialLipidomicsMaldiStudy", back_populates="metric_traces")
