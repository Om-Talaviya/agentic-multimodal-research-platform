"""SQLAlchemy models for Phase 227: Autonomous CRISPR-Cas12a Multiplex crRNA Array Self-Processing & Asymmetric Cleavage Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CrisprCas12aDirectRepeatProcessingStudy(Base):
    """Study record for Models Cas12a intrinsic endoribonuclease maturation kinetics of tandem direct repeat pre-crRNA arrays and simulates staggered 5-overhang target DNA cutting.."""

    __tablename__ = "cas12a_crrna_proc_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="crispr-cas12a-direct-repeat-processing")
    crrna_processing_efficiency_pct = Column(Float, nullable=False, default=98.2)
    collateral_ssdna_trans_cleavage_rate = Column(Float, nullable=False, default=8400.0)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CrisprCas12aDirectRepeatProcessingItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("CrisprCas12aDirectRepeatProcessingMetricTrace", back_populates="study", cascade="all, delete-orphan")


class CrisprCas12aDirectRepeatProcessingItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "cas12a_crrna_proc_item_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("cas12a_crrna_proc_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CrisprCas12aDirectRepeatProcessingStudy", back_populates="item_profiles")


class CrisprCas12aDirectRepeatProcessingMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "cas12a_crrna_proc_metric_traces"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("cas12a_crrna_proc_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CrisprCas12aDirectRepeatProcessingStudy", back_populates="metric_traces")
