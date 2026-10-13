"""SQLAlchemy models for Phase 449: Autonomous Microfluidic Droplet Single-Cell Metabolic Metabolomics Isotope Labeling Profiler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class DropletSingleCellIsotopeMetabolomicsStudy(Base):
    """Study record for Autonomous Microfluidic Droplet Single-Cell Metabolic Metabolomics Isotope Labeling Profiler."""

    __tablename__ = "p449_droplet_single_cell_isotope_metabolomics_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Glucose-13C6 Labeled Glioblastoma Stem-Like Cells in Monodisperse Fluorocarbon Droplets")
    analytical_modality = Column(String(100), nullable=False, default="single-cell-droplet-metabolomics")
    isotopic_enrichment_m3_lactate_ratio = Column(Float, nullable=False, default=0.765)
    droplet_generation_frequency_khz = Column(Float, nullable=False, default=4.8)
    glycolytic_flux_attomoles_per_cell_min = Column(Float, nullable=False, default=38.5)
    mass_accuracy_orbitrap_ppm = Column(Float, nullable=False, default=0.85)
    confidence_score = Column(Float, nullable=False, default=0.989)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("DropletSingleCellIsotopeMetabolomicsItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("DropletSingleCellIsotopeMetabolomicsMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class DropletSingleCellIsotopeMetabolomicsItemProfile(Base):
    """Detailed item profile for Autonomous Microfluidic Droplet Single-Cell Metabolic Metabolomics Isotope Labeling Profiler."""

    __tablename__ = "p449_droplet_single_cell_isotope_metabolomics_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p449_droplet_single_cell_isotope_metabolomics_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DropletSingleCellIsotopeMetabolomicsStudy", back_populates="item_profiles")


class DropletSingleCellIsotopeMetabolomicsMetricTrace(Base):
    """Metric trace for Autonomous Microfluidic Droplet Single-Cell Metabolic Metabolomics Isotope Labeling Profiler."""

    __tablename__ = "p449_droplet_single_cell_isotope_metabolomics_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p449_droplet_single_cell_isotope_metabolomics_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DropletSingleCellIsotopeMetabolomicsStudy", back_populates="metric_traces")
