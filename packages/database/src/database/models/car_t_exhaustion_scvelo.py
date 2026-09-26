"""SQLAlchemy models for Phase 220: Autonomous Single-Cell RNA Velocity Lineage Trajectory & CAR-T Epigenetic Exhaustion Interceptor Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CarTExhaustionScveloStudy(Base):
    """Study record for Simulates spliced-to-unspliced mRNA turnover kinetics to construct dynamic RNA velocity vectors, identifying critical branching points where CAR-T cells diverge into terminal exhaustion.."""

    __tablename__ = "car_t_scvelo_exhaust_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="car-t-exhaustion-scvelo")
    exhaustion_diversion_efficiency_pct = Column(Float, nullable=False, default=92.8)
    stem_memory_persistence_index = Column(Float, nullable=False, default=0.89)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CarTExhaustionScveloItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("CarTExhaustionScveloMetricTrace", back_populates="study", cascade="all, delete-orphan")


class CarTExhaustionScveloItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "car_t_scvelo_exhaust_item_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("car_t_scvelo_exhaust_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CarTExhaustionScveloStudy", back_populates="item_profiles")


class CarTExhaustionScveloMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "car_t_scvelo_exhaust_metric_traces"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("car_t_scvelo_exhaust_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CarTExhaustionScveloStudy", back_populates="metric_traces")
