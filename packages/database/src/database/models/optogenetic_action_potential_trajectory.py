"""SQLAlchemy models for Phase 444: Autonomous Optogenetic Membrane Depolarization & Action Potential Firing Trajectory Simulator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class OptogeneticActionPotentialStudy(Base):
    """Study record for Autonomous Optogenetic Membrane Depolarization & Action Potential Firing Trajectory Simulator."""

    __tablename__ = "p444_optogenetic_action_potential_trajectory_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Channelrhodopsin-2 (ChR2) Expressing Cortical Pyramidal Neurons under 470nm Pulsed Blue Light")
    analytical_modality = Column(String(100), nullable=False, default="optogenetic-membrane-depolarization")
    membrane_depolarization_rate_mv_per_ms = Column(Float, nullable=False, default=18.4)
    action_potential_firing_fidelity = Column(Float, nullable=False, default=0.982)
    photocurrent_amplitude_pA = Column(Float, nullable=False, default=840.0)
    channel_closing_decay_tau_off_ms = Column(Float, nullable=False, default=11.2)
    confidence_score = Column(Float, nullable=False, default=0.989)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("OptogeneticActionPotentialItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("OptogeneticActionPotentialMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class OptogeneticActionPotentialItemProfile(Base):
    """Detailed item profile for Autonomous Optogenetic Membrane Depolarization & Action Potential Firing Trajectory Simulator."""

    __tablename__ = "p444_optogenetic_action_potential_trajectory_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p444_optogenetic_action_potential_trajectory_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OptogeneticActionPotentialStudy", back_populates="item_profiles")


class OptogeneticActionPotentialMetricTrace(Base):
    """Metric trace for Autonomous Optogenetic Membrane Depolarization & Action Potential Firing Trajectory Simulator."""

    __tablename__ = "p444_optogenetic_action_potential_trajectory_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p444_optogenetic_action_potential_trajectory_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OptogeneticActionPotentialStudy", back_populates="metric_traces")
