"""SQLAlchemy models for Phase 352: Autonomous Multiplexed Ion Beam Imaging (MIBI-TOF) Deep Proteomic Spatial TME Deconvolver."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MibiTofSpatialProteomicsStudy(Base):
    """Study record for Processes secondary ion mass spectrometry time-of-flight isotopic channels to extract single-cell proteomic abundances, tertiary lymphoid structure boundaries, and immune checkpoints at 260nm lateral resolution.."""

    __tablename__ = "p352_mibi_tof_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="mibi-tof-spatial-proteomics")
    lateral_spatial_resolution_nanometers = Column(Float, nullable=False, default=260.0)
    isotopic_ion_channel_signal_to_noise_ratio = Column(Float, nullable=False, default=84.5)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MibiTofSpatialProteomicsItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("MibiTofSpatialProteomicsMetricTrace", back_populates="study", cascade="all, delete-orphan")


class MibiTofSpatialProteomicsItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "p352_mibi_tof_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p352_mibi_tof_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MibiTofSpatialProteomicsStudy", back_populates="item_profiles")


class MibiTofSpatialProteomicsMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "p352_mibi_tof_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p352_mibi_tof_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MibiTofSpatialProteomicsStudy", back_populates="metric_traces")
