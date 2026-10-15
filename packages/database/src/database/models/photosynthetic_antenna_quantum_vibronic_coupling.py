"""SQLAlchemy models for Phase 538: Autonomous Non-Markovian Quantum Vibronic Resonance Exciton Energy Transfer Simulator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class PhotosyntheticAntennaQuantumVibronicCouplingStudy(Base):
    """Study record for Autonomous Non-Markovian Quantum Vibronic Resonance Exciton Energy Transfer Simulator."""

    __tablename__ = "p538_photosynthetic_antenna_quantum_vibronic_coupling_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Light-Harvesting Complex II (LHCII) Trimer with 42 Chlorophyll Pigments embedded in Lipid Nanodisc")
    analytical_modality = Column(String(100), nullable=False, default="quantum-vibronic-exciton-dynamics")
    excitonic_energy_transfer_efficiency_pct = Column(Float, nullable=False, default=98.6)
    quantum_coherence_dephasing_time_fs = Column(Float, nullable=False, default=420.0)
    vibronic_resonance_coupling_cm_inv = Column(Float, nullable=False, default=148.0)
    spectral_density_reorganization_energy_cm_inv = Column(Float, nullable=False, default=65.0)
    confidence_score = Column(Float, nullable=False, default=0.995)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("PhotosyntheticAntennaQuantumVibronicCouplingItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("PhotosyntheticAntennaQuantumVibronicCouplingMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class PhotosyntheticAntennaQuantumVibronicCouplingItemProfile(Base):
    """Detailed item profile for Autonomous Non-Markovian Quantum Vibronic Resonance Exciton Energy Transfer Simulator."""

    __tablename__ = "p538_photosynthetic_antenna_quantum_vibronic_coupling_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p538_photosynthetic_antenna_quantum_vibronic_coupling_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("PhotosyntheticAntennaQuantumVibronicCouplingStudy", back_populates="item_profiles")


class PhotosyntheticAntennaQuantumVibronicCouplingMetricTrace(Base):
    """Metric trace for Autonomous Non-Markovian Quantum Vibronic Resonance Exciton Energy Transfer Simulator."""

    __tablename__ = "p538_photosynthetic_antenna_quantum_vibronic_coupling_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p538_photosynthetic_antenna_quantum_vibronic_coupling_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("PhotosyntheticAntennaQuantumVibronicCouplingStudy", back_populates="metric_traces")
