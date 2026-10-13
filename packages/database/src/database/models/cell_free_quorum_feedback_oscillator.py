"""SQLAlchemy models for Phase 454: Autonomous Synthetic Cell-Free Compartmentalized Gene Circuit Quorum Feedback Oscillator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CellFreeQuorumFeedbackOscillatorStudy(Base):
    """Study record for Autonomous Synthetic Cell-Free Compartmentalized Gene Circuit Quorum Feedback Oscillator."""

    __tablename__ = "p454_cell_free_quorum_feedback_oscillator_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Micro-Emulsion Lipid Vesicles with LuxI/LuxR Synthetic Transcriptional Auto-Inducer Network")
    analytical_modality = Column(String(100), nullable=False, default="cell-free-quorum-oscillator")
    quorum_oscillation_periodicity_hours = Column(Float, nullable=False, default=3.45)
    ahl_autoinducer_diffusion_flux_umol_cm2_s = Column(Float, nullable=False, default=0.082)
    inter_compartment_synchronization_index = Column(Float, nullable=False, default=0.945)
    circuit_persistence_lifetime_hours = Column(Float, nullable=False, default=42.0)
    confidence_score = Column(Float, nullable=False, default=0.987)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CellFreeQuorumFeedbackOscillatorItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("CellFreeQuorumFeedbackOscillatorMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class CellFreeQuorumFeedbackOscillatorItemProfile(Base):
    """Detailed item profile for Autonomous Synthetic Cell-Free Compartmentalized Gene Circuit Quorum Feedback Oscillator."""

    __tablename__ = "p454_cell_free_quorum_feedback_oscillator_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p454_cell_free_quorum_feedback_oscillator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CellFreeQuorumFeedbackOscillatorStudy", back_populates="item_profiles")


class CellFreeQuorumFeedbackOscillatorMetricTrace(Base):
    """Metric trace for Autonomous Synthetic Cell-Free Compartmentalized Gene Circuit Quorum Feedback Oscillator."""

    __tablename__ = "p454_cell_free_quorum_feedback_oscillator_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p454_cell_free_quorum_feedback_oscillator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CellFreeQuorumFeedbackOscillatorStudy", back_populates="metric_traces")
