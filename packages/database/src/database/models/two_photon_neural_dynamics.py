"""SQLAlchemy models for Phase 353: Autonomous Whole-Brain 2-Photon Calcium Imaging Neural Circuit Dynamics & Attractor Network Modeler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class TwoPhotonNeuralDynamicsStudy(Base):
    """Study record for Deconvolves continuous fluorescence traces from genetically encoded GCaMP8 indicators into spike train probability rasters and reconstructs non-linear manifold attractor dynamics across 50,000 cortical neurons.."""

    __tablename__ = "p353_neural_dyn_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="two-photon-neural-dynamics")
    spike_inference_temporal_precision_ms = Column(Float, nullable=False, default=4.5)
    neural_population_attractor_coherence_pct = Column(Float, nullable=False, default=96.2)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("TwoPhotonNeuralDynamicsItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("TwoPhotonNeuralDynamicsMetricTrace", back_populates="study", cascade="all, delete-orphan")


class TwoPhotonNeuralDynamicsItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "p353_neural_dyn_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p353_neural_dyn_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("TwoPhotonNeuralDynamicsStudy", back_populates="item_profiles")


class TwoPhotonNeuralDynamicsMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "p353_neural_dyn_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p353_neural_dyn_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("TwoPhotonNeuralDynamicsStudy", back_populates="metric_traces")
