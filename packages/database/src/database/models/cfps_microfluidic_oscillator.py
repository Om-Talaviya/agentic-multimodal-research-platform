"""SQLAlchemy models for Phase 425: Autonomous Cell-Free Protein TX-TL Compartmentalized Microfluidic Logic Oscillator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CfpsMicrofluidicOscillatorStudy(Base):
    """Study record for Autonomous Cell-Free Protein TX-TL Compartmentalized Microfluidic Logic Oscillator."""

    __tablename__ = "p425_cfps_microfluidic_oscillator_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Microfluidic Droplet Array with Repressilator TX-TL Reaction")
    analytical_modality = Column(String(100), nullable=False, default="cfps-microfluidic-oscillator")
    oscillation_period_minutes = Column(Float, nullable=False, default=124.0)
    fluorescent_reporter_amplitude_rfu = Column(Float, nullable=False, default=4850.0)
    reaction_dwell_stability_score = Column(Float, nullable=False, default=0.965)
    damping_decay_coefficient = Column(Float, nullable=False, default=0.042)
    confidence_score = Column(Float, nullable=False, default=0.983)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CfpsMicrofluidicOscillatorItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("CfpsMicrofluidicOscillatorMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class CfpsMicrofluidicOscillatorItemProfile(Base):
    """Detailed item profile for Autonomous Cell-Free Protein TX-TL Compartmentalized Microfluidic Logic Oscillator."""

    __tablename__ = "p425_cfps_microfluidic_oscillator_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p425_cfps_microfluidic_oscillator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CfpsMicrofluidicOscillatorStudy", back_populates="item_profiles")


class CfpsMicrofluidicOscillatorMetricTrace(Base):
    """Metric trace for Autonomous Cell-Free Protein TX-TL Compartmentalized Microfluidic Logic Oscillator."""

    __tablename__ = "p425_cfps_microfluidic_oscillator_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p425_cfps_microfluidic_oscillator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CfpsMicrofluidicOscillatorStudy", back_populates="metric_traces")
