"""SQLAlchemy models for Phase 540: Autonomous Diamond Nitrogen-Vacancy (NV) Center Quantum Defect Intracellular Thermal & Magnetic Sensor."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SingleMoleculeQuantumDefectSpinSensorStudy(Base):
    """Study record for Autonomous Diamond Nitrogen-Vacancy (NV) Center Quantum Defect Intracellular Thermal & Magnetic Sensor."""

    __tablename__ = "p540_single_molecule_quantum_defect_spin_sensor_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Fluorescent Nanodiamond with Single NV- Spin Defect internalized in Living Single Macrophage Cell")
    analytical_modality = Column(String(100), nullable=False, default="nv-center-quantum-sensing")
    magnetic_field_sensitivity_nT_sqrt_hz = Column(Float, nullable=False, default=12.4)
    intracellular_thermal_sensitivity_mK_sqrt_hz = Column(Float, nullable=False, default=45.0)
    spin_coherence_time_t2_us = Column(Float, nullable=False, default=185.0)
    odmr_spectral_contrast_pct = Column(Float, nullable=False, default=14.8)
    confidence_score = Column(Float, nullable=False, default=0.996)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SingleMoleculeQuantumDefectSpinSensorItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SingleMoleculeQuantumDefectSpinSensorMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SingleMoleculeQuantumDefectSpinSensorItemProfile(Base):
    """Detailed item profile for Autonomous Diamond Nitrogen-Vacancy (NV) Center Quantum Defect Intracellular Thermal & Magnetic Sensor."""

    __tablename__ = "p540_single_molecule_quantum_defect_spin_sensor_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p540_single_molecule_quantum_defect_spin_sensor_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SingleMoleculeQuantumDefectSpinSensorStudy", back_populates="item_profiles")


class SingleMoleculeQuantumDefectSpinSensorMetricTrace(Base):
    """Metric trace for Autonomous Diamond Nitrogen-Vacancy (NV) Center Quantum Defect Intracellular Thermal & Magnetic Sensor."""

    __tablename__ = "p540_single_molecule_quantum_defect_spin_sensor_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p540_single_molecule_quantum_defect_spin_sensor_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SingleMoleculeQuantumDefectSpinSensorStudy", back_populates="metric_traces")
