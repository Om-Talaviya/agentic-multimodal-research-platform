"""SQLAlchemy models for Phase 547: Autonomous Quantum Super-Resolution Single-Molecule Localization Microscopy (SMLM) Quantum State Squeezing Filter."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class QuantumSmlmLocalizationFilterStudy(Base):
    """Study record for Autonomous Quantum Super-Resolution Single-Molecule Localization Microscopy (SMLM) Quantum State Squeezing Filter."""

    __tablename__ = "p547_quantum_smlm_localization_filter_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Single AlexaFluor-647 Fluorophores in Sub-Diffraction Nanoscale DNA Origami Grid with Squeezed Vacuum State Illumination")
    analytical_modality = Column(String(100), nullable=False, default="quantum-smlm-squeezing")
    photon_localization_precision_nm = Column(Float, nullable=False, default=1.15)
    quantum_squeezing_shot_noise_reduction_db = Column(Float, nullable=False, default=4.2)
    point_spread_function_fisher_information = Column(Float, nullable=False, default=820.0)
    emitter_density_resolvable_per_um2 = Column(Float, nullable=False, default=185.0)
    confidence_score = Column(Float, nullable=False, default=0.996)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("QuantumSmlmLocalizationFilterItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("QuantumSmlmLocalizationFilterMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class QuantumSmlmLocalizationFilterItemProfile(Base):
    """Detailed item profile for Autonomous Quantum Super-Resolution Single-Molecule Localization Microscopy (SMLM) Quantum State Squeezing Filter."""

    __tablename__ = "p547_quantum_smlm_localization_filter_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p547_quantum_smlm_localization_filter_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("QuantumSmlmLocalizationFilterStudy", back_populates="item_profiles")


class QuantumSmlmLocalizationFilterMetricTrace(Base):
    """Metric trace for Autonomous Quantum Super-Resolution Single-Molecule Localization Microscopy (SMLM) Quantum State Squeezing Filter."""

    __tablename__ = "p547_quantum_smlm_localization_filter_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p547_quantum_smlm_localization_filter_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("QuantumSmlmLocalizationFilterStudy", back_populates="metric_traces")
