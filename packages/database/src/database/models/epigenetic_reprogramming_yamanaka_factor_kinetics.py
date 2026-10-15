"""SQLAlchemy models for Phase 546: Autonomous Stochastic Pioneer Transcription Factor Yamanaka Reprogramming Trajectory Predictor."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class EpigeneticReprogrammingYamanakaFactorKineticsStudy(Base):
    """Study record for Autonomous Stochastic Pioneer Transcription Factor Yamanaka Reprogramming Trajectory Predictor."""

    __tablename__ = "p546_epigenetic_reprogramming_yamanaka_factor_kinetics_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Single-Cell Doxycycline-Inducible OSKM Human Dermal Fibroblasts tracked across 21 Days")
    analytical_modality = Column(String(100), nullable=False, default="yamanaka-reprogramming-kinetics")
    fully_reprogrammed_naive_pluripotency_rate_pct = Column(Float, nullable=False, default=8.5)
    oct4_sox2_pioneer_chromatin_dwell_time_s = Column(Float, nullable=False, default=32.0)
    dna_methylation_clock_reversal_years = Column(Float, nullable=False, default=45.0)
    trajectory_waddington_barrier_crossing_prob = Column(Float, nullable=False, default=0.14)
    confidence_score = Column(Float, nullable=False, default=0.995)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("EpigeneticReprogrammingYamanakaFactorKineticsItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("EpigeneticReprogrammingYamanakaFactorKineticsMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class EpigeneticReprogrammingYamanakaFactorKineticsItemProfile(Base):
    """Detailed item profile for Autonomous Stochastic Pioneer Transcription Factor Yamanaka Reprogramming Trajectory Predictor."""

    __tablename__ = "p546_epigenetic_reprogramming_yamanaka_factor_kinetics_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p546_epigenetic_reprogramming_yamanaka_factor_kinetics_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("EpigeneticReprogrammingYamanakaFactorKineticsStudy", back_populates="item_profiles")


class EpigeneticReprogrammingYamanakaFactorKineticsMetricTrace(Base):
    """Metric trace for Autonomous Stochastic Pioneer Transcription Factor Yamanaka Reprogramming Trajectory Predictor."""

    __tablename__ = "p546_epigenetic_reprogramming_yamanaka_factor_kinetics_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p546_epigenetic_reprogramming_yamanaka_factor_kinetics_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("EpigeneticReprogrammingYamanakaFactorKineticsStudy", back_populates="metric_traces")
