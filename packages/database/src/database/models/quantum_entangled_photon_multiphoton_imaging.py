"""SQLAlchemy models for Phase 565: Autonomous Quantum Entangled Photon Biological Tissue Multiphoton Imaging Resolution Maximizer."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class QuantumEntangledPhotonMultiphotonImagingStudy(Base):
    """Study record for Autonomous Quantum Entangled Photon Biological Tissue Multiphoton Imaging Resolution Maximizer."""

    __tablename__ = "p565_quantum_entangled_photon_multiphoton_imaging_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Intact Vitrified Mouse Cortical Brain Slices illuminated with Polarization-Entangled Photon Pairs at 800nm")
    analytical_modality = Column(String(100), nullable=False, default="entangled-photon-multiphoton")
    two_photon_absorption_cross_section_enhancement_fold = Column(Float, nullable=False, default=185.0)
    imaging_tissue_penetration_depth_um = Column(Float, nullable=False, default=950.0)
    photobleaching_rate_suppression_pct = Column(Float, nullable=False, default=88.5)
    quantum_sub_shot_noise_snr_gain_db = Column(Float, nullable=False, default=5.4)
    confidence_score = Column(Float, nullable=False, default=0.998)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("QuantumEntangledPhotonMultiphotonImagingItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("QuantumEntangledPhotonMultiphotonImagingMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class QuantumEntangledPhotonMultiphotonImagingItemProfile(Base):
    """Detailed item profile for Autonomous Quantum Entangled Photon Biological Tissue Multiphoton Imaging Resolution Maximizer."""

    __tablename__ = "p565_quantum_entangled_photon_multiphoton_imaging_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p565_quantum_entangled_photon_multiphoton_imaging_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("QuantumEntangledPhotonMultiphotonImagingStudy", back_populates="item_profiles")


class QuantumEntangledPhotonMultiphotonImagingMetricTrace(Base):
    """Metric trace for Autonomous Quantum Entangled Photon Biological Tissue Multiphoton Imaging Resolution Maximizer."""

    __tablename__ = "p565_quantum_entangled_photon_multiphoton_imaging_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p565_quantum_entangled_photon_multiphoton_imaging_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("QuantumEntangledPhotonMultiphotonImagingStudy", back_populates="metric_traces")
