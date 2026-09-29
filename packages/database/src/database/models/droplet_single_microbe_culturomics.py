"""SQLAlchemy models for Phase 320: Autonomous Ultra-High-Throughput Droplet Microfluidic Unculturable Microbe Single-Cell Culturomics Screener."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class DropletSingleMicrobeCulturomicsStudy(Base):
    """Study record for Encapsulates unculturable environmental bacteria into picoliter water-in-oil droplets with fluorogenic metabolic sensors, isolating novel antibiotic-producing strains at millions/hour.."""

    __tablename__ = "droplet_culturomics_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="droplet-single-microbe-culturomics")
    droplet_screening_throughput_droplets_per_sec = Column(Float, nullable=False, default=2500.0)
    novel_uncultivated_species_recovery_rate_pct = Column(Float, nullable=False, default=74.5)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("DropletSingleMicrobeCulturomicsItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("DropletSingleMicrobeCulturomicsMetricTrace", back_populates="study", cascade="all, delete-orphan")


class DropletSingleMicrobeCulturomicsItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "droplet_culturomics_item_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("droplet_culturomics_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DropletSingleMicrobeCulturomicsStudy", back_populates="item_profiles")


class DropletSingleMicrobeCulturomicsMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "droplet_culturomics_metric_traces"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("droplet_culturomics_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DropletSingleMicrobeCulturomicsStudy", back_populates="metric_traces")
