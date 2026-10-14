"""SQLAlchemy models for Phase 478: Autonomous Solid-State Nanopore DNA Methylation Direct Ionic Current Discrimination Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class NanoporeDnaMethylationDiscriminationStudy(Base):
    """Study record for Autonomous Solid-State Nanopore DNA Methylation Direct Ionic Current Discrimination Engine."""

    __tablename__ = "p478_nanopore_dna_methylation_discrimination_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Sub-2nm Si3N4 Nanopore Translocating Native Synthetic 5mC / 5hmC Epigenetic DNA Duplexes")
    analytical_modality = Column(String(100), nullable=False, default="nanopore-methylation-discrimination")
    fractional_current_blockade_ratio = Column(Float, nullable=False, default=0.842)
    epigenetic_base_dwell_time_us = Column(Float, nullable=False, default=18.5)
    five_mc_vs_unmethylated_snr_db = Column(Float, nullable=False, default=14.8)
    single_base_resolution_confidence = Column(Float, nullable=False, default=0.988)
    confidence_score = Column(Float, nullable=False, default=0.991)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("NanoporeDnaMethylationDiscriminationItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("NanoporeDnaMethylationDiscriminationMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class NanoporeDnaMethylationDiscriminationItemProfile(Base):
    """Detailed item profile for Autonomous Solid-State Nanopore DNA Methylation Direct Ionic Current Discrimination Engine."""

    __tablename__ = "p478_nanopore_dna_methylation_discrimination_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p478_nanopore_dna_methylation_discrimination_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NanoporeDnaMethylationDiscriminationStudy", back_populates="item_profiles")


class NanoporeDnaMethylationDiscriminationMetricTrace(Base):
    """Metric trace for Autonomous Solid-State Nanopore DNA Methylation Direct Ionic Current Discrimination Engine."""

    __tablename__ = "p478_nanopore_dna_methylation_discrimination_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p478_nanopore_dna_methylation_discrimination_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NanoporeDnaMethylationDiscriminationStudy", back_populates="metric_traces")
