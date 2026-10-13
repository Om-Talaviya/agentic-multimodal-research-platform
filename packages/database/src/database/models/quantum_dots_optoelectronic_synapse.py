"""SQLAlchemy models for Phase 453: Autonomous Quantum Dots-Mediated Optoelectronic Neuromorphic Synaptic Potentiation Modeler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class QuantumDotsOptoelectronicSynapseStudy(Base):
    """Study record for Autonomous Quantum Dots-Mediated Optoelectronic Neuromorphic Synaptic Potentiation Modeler."""

    __tablename__ = "p453_quantum_dots_optoelectronic_synapse_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="InP/ZnS Core-Shell Quantum Dot Photo-Memristor Synapse Coupled to Primary Cortical Neurons")
    analytical_modality = Column(String(100), nullable=False, default="qd-optoelectronic-synapse")
    paired_pulse_facilitation_ppf_ratio = Column(Float, nullable=False, default=1.82)
    photocurrent_relaxation_lifetime_ms = Column(Float, nullable=False, default=245.0)
    synaptic_weight_plasticity_dynamic_range = Column(Float, nullable=False, default=4.65)
    energy_consumption_per_spike_femtojoules = Column(Float, nullable=False, default=82.0)
    confidence_score = Column(Float, nullable=False, default=0.991)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("QuantumDotsOptoelectronicSynapseItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("QuantumDotsOptoelectronicSynapseMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class QuantumDotsOptoelectronicSynapseItemProfile(Base):
    """Detailed item profile for Autonomous Quantum Dots-Mediated Optoelectronic Neuromorphic Synaptic Potentiation Modeler."""

    __tablename__ = "p453_quantum_dots_optoelectronic_synapse_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p453_quantum_dots_optoelectronic_synapse_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("QuantumDotsOptoelectronicSynapseStudy", back_populates="item_profiles")


class QuantumDotsOptoelectronicSynapseMetricTrace(Base):
    """Metric trace for Autonomous Quantum Dots-Mediated Optoelectronic Neuromorphic Synaptic Potentiation Modeler."""

    __tablename__ = "p453_quantum_dots_optoelectronic_synapse_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p453_quantum_dots_optoelectronic_synapse_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("QuantumDotsOptoelectronicSynapseStudy", back_populates="metric_traces")
