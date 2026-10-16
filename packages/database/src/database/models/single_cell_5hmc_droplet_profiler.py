"""SQLAlchemy models for Phase 550: Autonomous High-Throughput Droplet-Based Single-Cell Epigenomic DNA Hydroxymethylation (5hmC) Profiler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SingleCell5HmcDropletProfilerStudy(Base):
    """Study record for Autonomous High-Throughput Droplet-Based Single-Cell Epigenomic DNA Hydroxymethylation (5hmC) Profiler."""

    __tablename__ = "p550_single_cell_5hmc_droplet_profiler_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Single-Cell Microfluidic Barcoded Mouse Hippocampal Neurons subjected to T4 beta-Glucosyltransferase Glucosylation")
    analytical_modality = Column(String(100), nullable=False, default="droplet-epigenomic-5hmc")
    hydroxyl_methylated_cytosine_enrichment_fold = Column(Float, nullable=False, default=24.6)
    single_cell_epigenomic_capture_efficiency_pct = Column(Float, nullable=False, default=91.5)
    brain_active_enhancer_5hmc_density_per_kb = Column(Float, nullable=False, default=4.12)
    enzymatic_glucosylation_stoichiometry_pct = Column(Float, nullable=False, default=97.8)
    confidence_score = Column(Float, nullable=False, default=0.996)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SingleCell5HmcDropletProfilerItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SingleCell5HmcDropletProfilerMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SingleCell5HmcDropletProfilerItemProfile(Base):
    """Detailed item profile for Autonomous High-Throughput Droplet-Based Single-Cell Epigenomic DNA Hydroxymethylation (5hmC) Profiler."""

    __tablename__ = "p550_single_cell_5hmc_droplet_profiler_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p550_single_cell_5hmc_droplet_profiler_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SingleCell5HmcDropletProfilerStudy", back_populates="item_profiles")


class SingleCell5HmcDropletProfilerMetricTrace(Base):
    """Metric trace for Autonomous High-Throughput Droplet-Based Single-Cell Epigenomic DNA Hydroxymethylation (5hmC) Profiler."""

    __tablename__ = "p550_single_cell_5hmc_droplet_profiler_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p550_single_cell_5hmc_droplet_profiler_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SingleCell5HmcDropletProfilerStudy", back_populates="metric_traces")
