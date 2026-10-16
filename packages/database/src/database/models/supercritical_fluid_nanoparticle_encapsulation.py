"""SQLAlchemy models for Phase 555: Autonomous Microfluidic High-Pressure Supercritical Fluid Nanoparticle Encapsulation Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SupercriticalFluidNanoparticleEncapsulationStudy(Base):
    """Study record for Autonomous Microfluidic High-Pressure Supercritical Fluid Nanoparticle Encapsulation Engine."""

    __tablename__ = "p555_supercritical_fluid_nanoparticle_encapsulation_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Supercritical CO2 Rapid Expansion (RESS-SC) of PLGA-PEG Encapsulating Hydrophobic Paclitaxel and Cy5.5 Nanotracers")
    analytical_modality = Column(String(100), nullable=False, default="supercritical-fluid-nanoparticle")
    nanoparticle_mean_hydrodynamic_diameter_nm = Column(Float, nullable=False, default=68.5)
    encapsulation_efficiency_payload_pct = Column(Float, nullable=False, default=94.2)
    polydispersity_index_pdi = Column(Float, nullable=False, default=0.082)
    supercritical_operating_pressure_bar = Column(Float, nullable=False, default=185.0)
    confidence_score = Column(Float, nullable=False, default=0.995)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SupercriticalFluidNanoparticleEncapsulationItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SupercriticalFluidNanoparticleEncapsulationMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SupercriticalFluidNanoparticleEncapsulationItemProfile(Base):
    """Detailed item profile for Autonomous Microfluidic High-Pressure Supercritical Fluid Nanoparticle Encapsulation Engine."""

    __tablename__ = "p555_supercritical_fluid_nanoparticle_encapsulation_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p555_supercritical_fluid_nanoparticle_encapsulation_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SupercriticalFluidNanoparticleEncapsulationStudy", back_populates="item_profiles")


class SupercriticalFluidNanoparticleEncapsulationMetricTrace(Base):
    """Metric trace for Autonomous Microfluidic High-Pressure Supercritical Fluid Nanoparticle Encapsulation Engine."""

    __tablename__ = "p555_supercritical_fluid_nanoparticle_encapsulation_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p555_supercritical_fluid_nanoparticle_encapsulation_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SupercriticalFluidNanoparticleEncapsulationStudy", back_populates="metric_traces")
