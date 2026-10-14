"""SQLAlchemy models for Phase 488: Autonomous Cell-Free Compartmentalized Synthetic Transcription-Translation (TX-TL) Feedback Oscillator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SyntheticTxtlCompartmentalOscillatorStudy(Base):
    """Study record for Autonomous Cell-Free Compartmentalized Synthetic Transcription-Translation (TX-TL) Feedback Oscillator."""

    __tablename__ = "p488_synthetic_txtl_compartmental_oscillator_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Continuous Microfluidic Droplet-Exchanged E. coli Cell-Free Expression Matrix with Repressilator Circuit")
    analytical_modality = Column(String(100), nullable=False, default="txtl-compartmental-oscillator")
    oscillation_periodicity_hours = Column(Float, nullable=False, default=3.4)
    peak_to_trough_amplitude_fold_change = Column(Float, nullable=False, default=18.5)
    atp_regeneration_flux_mM_per_hr = Column(Float, nullable=False, default=1.8)
    oscillation_undamped_cycle_count = Column(Float, nullable=False, default=24.0)
    confidence_score = Column(Float, nullable=False, default=0.99)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SyntheticTxtlCompartmentalOscillatorItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SyntheticTxtlCompartmentalOscillatorMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SyntheticTxtlCompartmentalOscillatorItemProfile(Base):
    """Detailed item profile for Autonomous Cell-Free Compartmentalized Synthetic Transcription-Translation (TX-TL) Feedback Oscillator."""

    __tablename__ = "p488_synthetic_txtl_compartmental_oscillator_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p488_synthetic_txtl_compartmental_oscillator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SyntheticTxtlCompartmentalOscillatorStudy", back_populates="item_profiles")


class SyntheticTxtlCompartmentalOscillatorMetricTrace(Base):
    """Metric trace for Autonomous Cell-Free Compartmentalized Synthetic Transcription-Translation (TX-TL) Feedback Oscillator."""

    __tablename__ = "p488_synthetic_txtl_compartmental_oscillator_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p488_synthetic_txtl_compartmental_oscillator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SyntheticTxtlCompartmentalOscillatorStudy", back_populates="metric_traces")
