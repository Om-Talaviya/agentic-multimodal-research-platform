"""SQLAlchemy models for Phase 543: Autonomous Biomimetic Neuromorphic Optoelectronic Synapse Photo-Memristive Plasticity Forecaster."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class NeuromorphicOptogeneticSynapticEmulatorStudy(Base):
    """Study record for Autonomous Biomimetic Neuromorphic Optoelectronic Synapse Photo-Memristive Plasticity Forecaster."""

    __tablename__ = "p543_neuromorphic_optogenetic_synaptic_emulator_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="2D Transition Metal Dichalcogenide (MoS2) / Perovskite Heterostructure Optoelectronic Synaptic Memristor")
    analytical_modality = Column(String(100), nullable=False, default="optoelectronic-synapse-plasticity")
    paired_pulse_facilitation_ppf_index_pct = Column(Float, nullable=False, default=168.0)
    photo_induced_potentiation_energy_per_spike_fj = Column(Float, nullable=False, default=45.0)
    non_volatile_memory_retention_days = Column(Float, nullable=False, default=120.0)
    linear_weight_update_dynamic_range = Column(Float, nullable=False, default=4.8)
    confidence_score = Column(Float, nullable=False, default=0.994)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("NeuromorphicOptogeneticSynapticEmulatorItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("NeuromorphicOptogeneticSynapticEmulatorMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class NeuromorphicOptogeneticSynapticEmulatorItemProfile(Base):
    """Detailed item profile for Autonomous Biomimetic Neuromorphic Optoelectronic Synapse Photo-Memristive Plasticity Forecaster."""

    __tablename__ = "p543_neuromorphic_optogenetic_synaptic_emulator_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p543_neuromorphic_optogenetic_synaptic_emulator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NeuromorphicOptogeneticSynapticEmulatorStudy", back_populates="item_profiles")


class NeuromorphicOptogeneticSynapticEmulatorMetricTrace(Base):
    """Metric trace for Autonomous Biomimetic Neuromorphic Optoelectronic Synapse Photo-Memristive Plasticity Forecaster."""

    __tablename__ = "p543_neuromorphic_optogenetic_synaptic_emulator_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p543_neuromorphic_optogenetic_synaptic_emulator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NeuromorphicOptogeneticSynapticEmulatorStudy", back_populates="metric_traces")
