"""SQLAlchemy models for Phase 291: Autonomous CRISPR-Cas12a (Cpf1) Multiplexed Trans-Cleavage Single-Nucleotide Polymorphism Sentinel."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CrisprCas12aMultiplexedSnpStudy(Base):
    """Study record for Models Cas12a target activation, non-specific ssDNA collateral cleavage, and TTTV PAM compatibility for multiplexed single-nucleotide polymorphism discrimination.."""

    __tablename__ = "cas12a_snp_sentinel_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="crispr-cas12a-multiplexed-snp")
    single_nucleotide_discrimination_ratio = Column(Float, nullable=False, default=56.4)
    ssdna_trans_cleavage_rate_kcat_km = Column(Float, nullable=False, default=14000000.0)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CrisprCas12aMultiplexedSnpItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("CrisprCas12aMultiplexedSnpMetricTrace", back_populates="study", cascade="all, delete-orphan")


class CrisprCas12aMultiplexedSnpItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "cas12a_snp_sentinel_item_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("cas12a_snp_sentinel_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CrisprCas12aMultiplexedSnpStudy", back_populates="item_profiles")


class CrisprCas12aMultiplexedSnpMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "cas12a_snp_sentinel_metric_traces"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("cas12a_snp_sentinel_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CrisprCas12aMultiplexedSnpStudy", back_populates="metric_traces")
