"""SQLAlchemy models for Phase 501: Autonomous CRISPR-Associated Transposase (CAST) Targeted Large Genomic Cargo Integrator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CastTransposaseGenomicIntegrationStudy(Base):
    """Study record for Autonomous CRISPR-Associated Transposase (CAST) Targeted Large Genomic Cargo Integrator."""

    __tablename__ = "p501_cast_transposase_genomic_integration_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Type V-K CRISPR-Cas12k / TnsA-TnsB-TnsC Transposase Complex with 10kb Cargo Plasmid in Human Cells")
    analytical_modality = Column(String(100), nullable=False, default="cast-transposase-integration")
    targeted_insertion_efficiency_pct = Column(Float, nullable=False, default=68.5)
    on_target_integration_accuracy_pct = Column(Float, nullable=False, default=99.2)
    cargo_payload_size_capacity_kb = Column(Float, nullable=False, default=10.0)
    indel_free_junction_preservation_ratio = Column(Float, nullable=False, default=0.985)
    confidence_score = Column(Float, nullable=False, default=0.994)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CastTransposaseGenomicIntegrationItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("CastTransposaseGenomicIntegrationMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class CastTransposaseGenomicIntegrationItemProfile(Base):
    """Detailed item profile for Autonomous CRISPR-Associated Transposase (CAST) Targeted Large Genomic Cargo Integrator."""

    __tablename__ = "p501_cast_transposase_genomic_integration_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p501_cast_transposase_genomic_integration_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CastTransposaseGenomicIntegrationStudy", back_populates="item_profiles")


class CastTransposaseGenomicIntegrationMetricTrace(Base):
    """Metric trace for Autonomous CRISPR-Associated Transposase (CAST) Targeted Large Genomic Cargo Integrator."""

    __tablename__ = "p501_cast_transposase_genomic_integration_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p501_cast_transposase_genomic_integration_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CastTransposaseGenomicIntegrationStudy", back_populates="metric_traces")
