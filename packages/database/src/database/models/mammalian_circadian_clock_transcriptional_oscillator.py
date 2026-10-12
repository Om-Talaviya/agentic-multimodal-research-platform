"""SQLAlchemy models for Phase 442: Autonomous Mammalian Circadian Transcriptional-Translational Feedback Loop (TTFL) Limit Cycle Simulator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MammalianCircadianClockStudy(Base):
    """Study record for Autonomous Mammalian Circadian Transcriptional-Translational Feedback Loop (TTFL) Limit Cycle Simulator."""

    __tablename__ = "p442_mammalian_circadian_clock_transcriptional_oscillator_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Suprachiasmatic Nucleus (SCN) Single-Cell CLOCK:BMAL1 / PER:CRY Pacemaker Circuit")
    analytical_modality = Column(String(100), nullable=False, default="circadian-ttfl-oscillator")
    free_running_period_tau_hours = Column(Float, nullable=False, default=24.15)
    oscillation_amplitude_per2_mrna_ratio = Column(Float, nullable=False, default=4.82)
    phase_response_shift_hours = Column(Float, nullable=False, default=-2.4)
    limit_cycle_bifurcation_stability = Column(Float, nullable=False, default=0.978)
    confidence_score = Column(Float, nullable=False, default=0.987)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MammalianCircadianClockItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MammalianCircadianClockMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MammalianCircadianClockItemProfile(Base):
    """Detailed item profile for Autonomous Mammalian Circadian Transcriptional-Translational Feedback Loop (TTFL) Limit Cycle Simulator."""

    __tablename__ = "p442_mammalian_circadian_clock_transcriptional_oscillator_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p442_mammalian_circadian_clock_transcriptional_oscillator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MammalianCircadianClockStudy", back_populates="item_profiles")


class MammalianCircadianClockMetricTrace(Base):
    """Metric trace for Autonomous Mammalian Circadian Transcriptional-Translational Feedback Loop (TTFL) Limit Cycle Simulator."""

    __tablename__ = "p442_mammalian_circadian_clock_transcriptional_oscillator_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p442_mammalian_circadian_clock_transcriptional_oscillator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MammalianCircadianClockStudy", back_populates="metric_traces")
