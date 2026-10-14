"""SQLAlchemy models for Phase 502: Autonomous Microfluidic Acoustic Sorting & Droplet Single-Exosome Surface Tetraspanin Profiler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class AcousticDropletSingleExosomeProfilerStudy(Base):
    """Study record for Autonomous Microfluidic Acoustic Sorting & Droplet Single-Exosome Surface Tetraspanin Profiler."""

    __tablename__ = "p502_acoustic_droplet_single_exosome_profiler_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Surface Acoustic Wave (SAW) Focused Patient Plasma with CD63/CD81/CD9 Fluorophore Micro-Beads")
    analytical_modality = Column(String(100), nullable=False, default="acoustic-droplet-single-exosome")
    exosome_acoustic_separation_purity_pct = Column(Float, nullable=False, default=96.8)
    droplet_single_vesicle_encapsulation_lambda = Column(Float, nullable=False, default=0.28)
    tetraspanin_triplet_colocalization_score = Column(Float, nullable=False, default=0.915)
    low_abundant_cargo_detection_limit_fM = Column(Float, nullable=False, default=15.0)
    confidence_score = Column(Float, nullable=False, default=0.99)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("AcousticDropletSingleExosomeProfilerItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("AcousticDropletSingleExosomeProfilerMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class AcousticDropletSingleExosomeProfilerItemProfile(Base):
    """Detailed item profile for Autonomous Microfluidic Acoustic Sorting & Droplet Single-Exosome Surface Tetraspanin Profiler."""

    __tablename__ = "p502_acoustic_droplet_single_exosome_profiler_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p502_acoustic_droplet_single_exosome_profiler_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("AcousticDropletSingleExosomeProfilerStudy", back_populates="item_profiles")


class AcousticDropletSingleExosomeProfilerMetricTrace(Base):
    """Metric trace for Autonomous Microfluidic Acoustic Sorting & Droplet Single-Exosome Surface Tetraspanin Profiler."""

    __tablename__ = "p502_acoustic_droplet_single_exosome_profiler_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p502_acoustic_droplet_single_exosome_profiler_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("AcousticDropletSingleExosomeProfilerStudy", back_populates="metric_traces")
