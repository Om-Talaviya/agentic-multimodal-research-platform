"""SQLAlchemy models for Phase 521: Autonomous Biomolecular Protein Nanofiber Memristive Synaptic Weight Plasticity Forecaster."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class NeuromorphicMemristiveSynapseProteinStudy(Base):
    """Study record for Autonomous Biomolecular Protein Nanofiber Memristive Synaptic Weight Plasticity Forecaster."""

    __tablename__ = "p521_neuromorphic_memristive_synapse_protein_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Crossbar Array of Self-Assembled Amyloid-beta / Ferritin Bio-Nanowires sandwiched between Pt/Au Electrodes")
    analytical_modality = Column(String(100), nullable=False, default="biomolecular-memristor-plasticity")
    conductance_switching_on_off_ratio = Column(Float, nullable=False, default=185.0)
    spike_timing_dependent_plasticity_stdp_tau_ms = Column(Float, nullable=False, default=24.5)
    analog_conductance_states_count = Column(Float, nullable=False, default=64.0)
    endurance_switching_cycles = Column(Float, nullable=False, default=50000.0)
    confidence_score = Column(Float, nullable=False, default=0.992)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("NeuromorphicMemristiveSynapseProteinItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("NeuromorphicMemristiveSynapseProteinMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class NeuromorphicMemristiveSynapseProteinItemProfile(Base):
    """Detailed item profile for Autonomous Biomolecular Protein Nanofiber Memristive Synaptic Weight Plasticity Forecaster."""

    __tablename__ = "p521_neuromorphic_memristive_synapse_protein_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p521_neuromorphic_memristive_synapse_protein_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NeuromorphicMemristiveSynapseProteinStudy", back_populates="item_profiles")


class NeuromorphicMemristiveSynapseProteinMetricTrace(Base):
    """Metric trace for Autonomous Biomolecular Protein Nanofiber Memristive Synaptic Weight Plasticity Forecaster."""

    __tablename__ = "p521_neuromorphic_memristive_synapse_protein_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p521_neuromorphic_memristive_synapse_protein_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NeuromorphicMemristiveSynapseProteinStudy", back_populates="metric_traces")
