"""SQLAlchemy models for Phase 535: Autonomous Multi-Tier Synthetic Epigenetic CRISPR Reversible Silencing Transcriptional Memory Cascade."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SyntheticEpigeneticCrisprMemoryCascadeStudy(Base):
    """Study record for Autonomous Multi-Tier Synthetic Epigenetic CRISPR Reversible Silencing Transcriptional Memory Cascade."""

    __tablename__ = "p535_synthetic_epigenetic_crispr_memory_cascade_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Engineered dCas9-KRAB-MeCP2 & dCas9-TET1 Autocatalytic Feedback Toggle in Human iPSCs")
    analytical_modality = Column(String(100), nullable=False, default="crispr-epigenetic-memory-cascade")
    transcriptional_repression_half_life_days = Column(Float, nullable=False, default=42.0)
    h3k9me3_deposition_spreading_kb = Column(Float, nullable=False, default=4.8)
    epigenetic_memory_heritability_generations = Column(Float, nullable=False, default=35.0)
    reversible_reactivation_efficiency_pct = Column(Float, nullable=False, default=94.5)
    confidence_score = Column(Float, nullable=False, default=0.995)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SyntheticEpigeneticCrisprMemoryCascadeItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SyntheticEpigeneticCrisprMemoryCascadeMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SyntheticEpigeneticCrisprMemoryCascadeItemProfile(Base):
    """Detailed item profile for Autonomous Multi-Tier Synthetic Epigenetic CRISPR Reversible Silencing Transcriptional Memory Cascade."""

    __tablename__ = "p535_synthetic_epigenetic_crispr_memory_cascade_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p535_synthetic_epigenetic_crispr_memory_cascade_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SyntheticEpigeneticCrisprMemoryCascadeStudy", back_populates="item_profiles")


class SyntheticEpigeneticCrisprMemoryCascadeMetricTrace(Base):
    """Metric trace for Autonomous Multi-Tier Synthetic Epigenetic CRISPR Reversible Silencing Transcriptional Memory Cascade."""

    __tablename__ = "p535_synthetic_epigenetic_crispr_memory_cascade_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p535_synthetic_epigenetic_crispr_memory_cascade_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SyntheticEpigeneticCrisprMemoryCascadeStudy", back_populates="metric_traces")
