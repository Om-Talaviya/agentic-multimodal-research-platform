"""SQLAlchemy models for Phase 509: Autonomous Ultra-Weak Biophoton Emission & Mitochondrial ROS Chemiluminescence Forecaster."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class QuantumBiophotonMitochondrialEmissionStudy(Base):
    """Study record for Autonomous Ultra-Weak Biophoton Emission & Mitochondrial ROS Chemiluminescence Forecaster."""

    __tablename__ = "p509_quantum_biophoton_mitochondrial_emission_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Permeabilized Primary Cortical Neurons in Cryogenic Photomultiplier Chamber under Glutamate Stress")
    analytical_modality = Column(String(100), nullable=False, default="ultra-weak-biophoton-chemiluminescence")
    ultra_weak_photon_count_cps_per_cm2 = Column(Float, nullable=False, default=14.8)
    singlet_oxygen_decay_spectral_emission_nm = Column(Float, nullable=False, default=1270.0)
    lipid_peroxy_chemiluminescence_quantum_yield = Column(Float, nullable=False, default=8.5e-05)
    respiratory_chain_complex_leak_correlation = Column(Float, nullable=False, default=0.912)
    confidence_score = Column(Float, nullable=False, default=0.989)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("QuantumBiophotonMitochondrialEmissionItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("QuantumBiophotonMitochondrialEmissionMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class QuantumBiophotonMitochondrialEmissionItemProfile(Base):
    """Detailed item profile for Autonomous Ultra-Weak Biophoton Emission & Mitochondrial ROS Chemiluminescence Forecaster."""

    __tablename__ = "p509_quantum_biophoton_mitochondrial_emission_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p509_quantum_biophoton_mitochondrial_emission_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("QuantumBiophotonMitochondrialEmissionStudy", back_populates="item_profiles")


class QuantumBiophotonMitochondrialEmissionMetricTrace(Base):
    """Metric trace for Autonomous Ultra-Weak Biophoton Emission & Mitochondrial ROS Chemiluminescence Forecaster."""

    __tablename__ = "p509_quantum_biophoton_mitochondrial_emission_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p509_quantum_biophoton_mitochondrial_emission_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("QuantumBiophotonMitochondrialEmissionStudy", back_populates="metric_traces")
