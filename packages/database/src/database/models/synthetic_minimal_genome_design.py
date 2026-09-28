"""SQLAlchemy models for Phase 265: Autonomous Synthetic Minimal Genome Design & Metabolic Essentiality Minimization Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SyntheticMinimalGenomeDesignStudy(Base):
    """Study record for Designs synthetic minimal bacterial genomes via flux balance analysis and quasi-essential gene clustering, reducing genome size while preserving metabolic self-sufficiency.."""

    __tablename__ = "syn_minimal_genome_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="synthetic-minimal-genome-design")
    genome_size_reduction_ratio_pct = Column(Float, nullable=False, default=54.2)
    metabolic_viability_simulation_score = Column(Float, nullable=False, default=98.2)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SyntheticMinimalGenomeDesignItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("SyntheticMinimalGenomeDesignMetricTrace", back_populates="study", cascade="all, delete-orphan")


class SyntheticMinimalGenomeDesignItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "syn_minimal_genome_item_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("syn_minimal_genome_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SyntheticMinimalGenomeDesignStudy", back_populates="item_profiles")


class SyntheticMinimalGenomeDesignMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "syn_minimal_genome_metric_traces"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("syn_minimal_genome_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SyntheticMinimalGenomeDesignStudy", back_populates="metric_traces")
