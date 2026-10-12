"""SQLAlchemy models for Phase 432: Autonomous Continuous Directed Evolution PACE (Phage-Assisted Continuous Evolution) Fitness Trajectory Modeler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class PaceDirectedEvolutionTrajectoryStudy(Base):
    """Study record for Autonomous Continuous Directed Evolution PACE (Phage-Assisted Continuous Evolution) Fitness Trajectory Modeler."""

    __tablename__ = "p432_pace_directed_evolution_trajectory_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Continuous Chemostat Lago Lagoon Phage Population")
    analytical_modality = Column(String(100), nullable=False, default="pace-directed-evolution")
    selection_stringency_factor = Column(Float, nullable=False, default=4.85)
    mutational_drift_velocity_subs_per_hr = Column(Float, nullable=False, default=0.32)
    fitness_enrichment_trajectory_fold = Column(Float, nullable=False, default=84.0)
    lagoon_dilution_rate_vol_per_hr = Column(Float, nullable=False, default=2.1)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("PaceDirectedEvolutionTrajectoryItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("PaceDirectedEvolutionTrajectoryMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class PaceDirectedEvolutionTrajectoryItemProfile(Base):
    """Detailed item profile for Autonomous Continuous Directed Evolution PACE (Phage-Assisted Continuous Evolution) Fitness Trajectory Modeler."""

    __tablename__ = "p432_pace_directed_evolution_trajectory_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p432_pace_directed_evolution_trajectory_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("PaceDirectedEvolutionTrajectoryStudy", back_populates="item_profiles")


class PaceDirectedEvolutionTrajectoryMetricTrace(Base):
    """Metric trace for Autonomous Continuous Directed Evolution PACE (Phage-Assisted Continuous Evolution) Fitness Trajectory Modeler."""

    __tablename__ = "p432_pace_directed_evolution_trajectory_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p432_pace_directed_evolution_trajectory_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("PaceDirectedEvolutionTrajectoryStudy", back_populates="metric_traces")
