"""SQLAlchemy models for Phase 441: Autonomous Fenna-Matthews-Olson (FMO) Complex Quantum Exciton Energy Transfer & Coherence Modeler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class PhotosystemQuantumCoherenceStudy(Base):
    """Study record for Autonomous Fenna-Matthews-Olson (FMO) Complex Quantum Exciton Energy Transfer & Coherence Modeler."""

    __tablename__ = "p441_photosystem_quantum_coherence_exciton_fmo_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Green Sulfur Bacteria Chlorobium tepidum FMO Bacteriochlorophyll Trimer")
    analytical_modality = Column(String(100), nullable=False, default="quantum-exciton-fmo")
    exciton_transfer_efficiency_ratio = Column(Float, nullable=False, default=0.991)
    quantum_coherence_lifetime_fs = Column(Float, nullable=False, default=420.0)
    site_energy_disorder_cm_inv = Column(Float, nullable=False, default=85.0)
    sink_bchl_trapping_rate_ps_inv = Column(Float, nullable=False, default=1.85)
    confidence_score = Column(Float, nullable=False, default=0.989)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("PhotosystemQuantumCoherenceItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("PhotosystemQuantumCoherenceMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class PhotosystemQuantumCoherenceItemProfile(Base):
    """Detailed item profile for Autonomous Fenna-Matthews-Olson (FMO) Complex Quantum Exciton Energy Transfer & Coherence Modeler."""

    __tablename__ = "p441_photosystem_quantum_coherence_exciton_fmo_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p441_photosystem_quantum_coherence_exciton_fmo_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("PhotosystemQuantumCoherenceStudy", back_populates="item_profiles")


class PhotosystemQuantumCoherenceMetricTrace(Base):
    """Metric trace for Autonomous Fenna-Matthews-Olson (FMO) Complex Quantum Exciton Energy Transfer & Coherence Modeler."""

    __tablename__ = "p441_photosystem_quantum_coherence_exciton_fmo_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p441_photosystem_quantum_coherence_exciton_fmo_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("PhotosystemQuantumCoherenceStudy", back_populates="metric_traces")
