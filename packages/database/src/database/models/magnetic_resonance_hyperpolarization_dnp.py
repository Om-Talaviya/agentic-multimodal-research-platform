"""SQLAlchemy models for Phase 529: Autonomous Dissolution Dynamic Nuclear Polarization (DNP) Hyperpolarized Carbon-13 Flux Tracer."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MagneticResonanceHyperpolarizationDnpStudy(Base):
    """Study record for Autonomous Dissolution Dynamic Nuclear Polarization (DNP) Hyperpolarized Carbon-13 Flux Tracer."""

    __tablename__ = "p529_magnetic_resonance_hyperpolarization_dnp_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Hyperpolarized [1-13C] Pyruvate with Trityl Radical OX063 Polarized at 1.4K and 5T")
    analytical_modality = Column(String(100), nullable=False, default="dnp-hyperpolarized-nmr-flux")
    carbon_13_nuclear_polarization_pct = Column(Float, nullable=False, default=46.8)
    in_vivo_t1_relaxation_time_s = Column(Float, nullable=False, default=45.2)
    pyruvate_to_lactate_apparent_flux_rate_k_pl = Column(Float, nullable=False, default=0.078)
    spectroscopic_snr_enhancement_factor = Column(Float, nullable=False, default=14500.0)
    confidence_score = Column(Float, nullable=False, default=0.995)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MagneticResonanceHyperpolarizationDnpItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MagneticResonanceHyperpolarizationDnpMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MagneticResonanceHyperpolarizationDnpItemProfile(Base):
    """Detailed item profile for Autonomous Dissolution Dynamic Nuclear Polarization (DNP) Hyperpolarized Carbon-13 Flux Tracer."""

    __tablename__ = "p529_magnetic_resonance_hyperpolarization_dnp_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p529_magnetic_resonance_hyperpolarization_dnp_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MagneticResonanceHyperpolarizationDnpStudy", back_populates="item_profiles")


class MagneticResonanceHyperpolarizationDnpMetricTrace(Base):
    """Metric trace for Autonomous Dissolution Dynamic Nuclear Polarization (DNP) Hyperpolarized Carbon-13 Flux Tracer."""

    __tablename__ = "p529_magnetic_resonance_hyperpolarization_dnp_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p529_magnetic_resonance_hyperpolarization_dnp_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MagneticResonanceHyperpolarizationDnpStudy", back_populates="metric_traces")
