"""SQLAlchemy models for Phase 312: Autonomous Molecular DNA Digital Data Storage High-Density Synthesis & Nanopore Ionic Translocation Codec."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class NanoporeDnaStorageCodecStudy(Base):
    """Study record for Encodes binary petabyte datasets into GC-balanced, homopolymer-free synthetic oligo pools and decodes ionic translocation current signatures with error-correcting Reed-Solomon/Fountain algorithms.."""

    __tablename__ = "dna_storage_codec_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="nanopore-dna-storage-codec")
    dna_storage_information_density_bits_per_nucleotide = Column(Float, nullable=False, default=1.96)
    raw_translocation_bit_error_rate_pct = Column(Float, nullable=False, default=1.25)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("NanoporeDnaStorageCodecItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("NanoporeDnaStorageCodecMetricTrace", back_populates="study", cascade="all, delete-orphan")


class NanoporeDnaStorageCodecItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "dna_storage_codec_item_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("dna_storage_codec_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NanoporeDnaStorageCodecStudy", back_populates="item_profiles")


class NanoporeDnaStorageCodecMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "dna_storage_codec_metric_traces"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("dna_storage_codec_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NanoporeDnaStorageCodecStudy", back_populates="metric_traces")
