"""SQLAlchemy models for Phase 326: Autonomous PACE (Phage-Assisted Continuous Evolution) Dynamic Turbidostat Selection Feedback Controller."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class ContinuousEvolutionPacmanBioreactorStudy(Base):
    """Study record for Controls mutagenesis plasmid expression, phage dilution wash-out rates, and host selection stringency in continuous automated bioreactors for hyper-accelerated enzyme evolution.."""

    __tablename__ = "continuous_evolution_pace_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="continuous-evolution-pacman")
    evolved_enzyme_catalytic_efficiency_kcat_km_fold_improvement = Column(Float, nullable=False, default=185.0)
    evolution_cycle_generations_per_day = Column(Float, nullable=False, default=36.0)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("ContinuousEvolutionPacmanBioreactorItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("ContinuousEvolutionPacmanBioreactorMetricTrace", back_populates="study", cascade="all, delete-orphan")


class ContinuousEvolutionPacmanBioreactorItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "continuous_evolution_pace_item_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("continuous_evolution_pace_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("ContinuousEvolutionPacmanBioreactorStudy", back_populates="item_profiles")


class ContinuousEvolutionPacmanBioreactorMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "continuous_evolution_pace_metric_traces"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("continuous_evolution_pace_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("ContinuousEvolutionPacmanBioreactorStudy", back_populates="metric_traces")
