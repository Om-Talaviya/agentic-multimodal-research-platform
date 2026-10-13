"""SQLAlchemy models for Phase 452: Autonomous Microtubule Spindle Assembly Checkpoint (SAC) Mitotic Tension Kinetic Simulator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MitoticSpindleSacTensionStudy(Base):
    """Study record for Autonomous Microtubule Spindle Assembly Checkpoint (SAC) Mitotic Tension Kinetic Simulator."""

    __tablename__ = "p452_mitotic_spindle_sac_tension_simulator_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Bipolar Mitotic Kinetochore-Microtubule Interface with Mad2/BubR1 Checkpoint Sensor")
    analytical_modality = Column(String(100), nullable=False, default="spindle-assembly-sac-kinetics")
    kinetochore_tension_pico_newtons = Column(Float, nullable=False, default=38.5)
    mad2_activation_rate_constant_s_inv = Column(Float, nullable=False, default=0.045)
    anaphase_onset_delay_minutes = Column(Float, nullable=False, default=18.2)
    spindle_bipolar_alignment_coherence = Column(Float, nullable=False, default=0.965)
    confidence_score = Column(Float, nullable=False, default=0.988)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MitoticSpindleSacTensionItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MitoticSpindleSacTensionMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MitoticSpindleSacTensionItemProfile(Base):
    """Detailed item profile for Autonomous Microtubule Spindle Assembly Checkpoint (SAC) Mitotic Tension Kinetic Simulator."""

    __tablename__ = "p452_mitotic_spindle_sac_tension_simulator_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p452_mitotic_spindle_sac_tension_simulator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MitoticSpindleSacTensionStudy", back_populates="item_profiles")


class MitoticSpindleSacTensionMetricTrace(Base):
    """Metric trace for Autonomous Microtubule Spindle Assembly Checkpoint (SAC) Mitotic Tension Kinetic Simulator."""

    __tablename__ = "p452_mitotic_spindle_sac_tension_simulator_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p452_mitotic_spindle_sac_tension_simulator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MitoticSpindleSacTensionStudy", back_populates="metric_traces")
