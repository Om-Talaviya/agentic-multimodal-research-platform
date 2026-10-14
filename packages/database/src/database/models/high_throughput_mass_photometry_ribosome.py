"""SQLAlchemy models for Phase 516: Autonomous Automated High-Throughput Mass Photometry Macromolecular Mass Dispersity Profiler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class HighThroughputMassPhotometryRibosomeStudy(Base):
    """Study record for Autonomous Automated High-Throughput Mass Photometry Macromolecular Mass Dispersity Profiler."""

    __tablename__ = "p516_high_throughput_mass_photometry_ribosome_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Label-Free Reconstituted 70S Ribosome Assembly Intermediates with Initiation Factors IF1/IF2/IF3")
    analytical_modality = Column(String(100), nullable=False, default="mass-photometry-single-molecule-scattering")
    molecular_mass_resolution_error_pct = Column(Float, nullable=False, default=1.25)
    subassembly_stoichiometric_ratio_30s_50s_70s = Column(Float, nullable=False, default=1.05)
    single_molecule_scattering_interferometric_contrast = Column(Float, nullable=False, default=0.0085)
    sample_consumption_volume_nanoliters = Column(Float, nullable=False, default=50.0)
    confidence_score = Column(Float, nullable=False, default=0.994)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("HighThroughputMassPhotometryRibosomeItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("HighThroughputMassPhotometryRibosomeMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class HighThroughputMassPhotometryRibosomeItemProfile(Base):
    """Detailed item profile for Autonomous Automated High-Throughput Mass Photometry Macromolecular Mass Dispersity Profiler."""

    __tablename__ = "p516_high_throughput_mass_photometry_ribosome_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p516_high_throughput_mass_photometry_ribosome_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("HighThroughputMassPhotometryRibosomeStudy", back_populates="item_profiles")


class HighThroughputMassPhotometryRibosomeMetricTrace(Base):
    """Metric trace for Autonomous Automated High-Throughput Mass Photometry Macromolecular Mass Dispersity Profiler."""

    __tablename__ = "p516_high_throughput_mass_photometry_ribosome_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p516_high_throughput_mass_photometry_ribosome_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("HighThroughputMassPhotometryRibosomeStudy", back_populates="metric_traces")
