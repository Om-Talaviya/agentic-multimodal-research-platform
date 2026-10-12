"""SQLAlchemy models for Phase 437: Autonomous Microbial Electrogenic Biofilm Extracellular Electron Transfer (EET) Simulator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MicrobialElectrogenicBiofilmStudy(Base):
    """Study record for Autonomous Microbial Electrogenic Biofilm Extracellular Electron Transfer (EET) Simulator."""

    __tablename__ = "p437_microbial_electrogenic_biofilm_flux_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Shewanella oneidensis MR-1 Anode Biofilm with Multi-Heme Cytochrome Array")
    analytical_modality = Column(String(100), nullable=False, default="microbial-eet-biofilm")
    current_density_mA_per_cm2 = Column(Float, nullable=False, default=1.42)
    cytochrome_conduction_rate_electrons_per_s = Column(Float, nullable=False, default=1240.0)
    redox_potential_gradient_mV = Column(Float, nullable=False, default=-280.0)
    biofilm_coulombic_efficiency = Column(Float, nullable=False, default=0.895)
    confidence_score = Column(Float, nullable=False, default=0.986)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MicrobialElectrogenicBiofilmItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MicrobialElectrogenicBiofilmMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MicrobialElectrogenicBiofilmItemProfile(Base):
    """Detailed item profile for Autonomous Microbial Electrogenic Biofilm Extracellular Electron Transfer (EET) Simulator."""

    __tablename__ = "p437_microbial_electrogenic_biofilm_flux_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p437_microbial_electrogenic_biofilm_flux_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MicrobialElectrogenicBiofilmStudy", back_populates="item_profiles")


class MicrobialElectrogenicBiofilmMetricTrace(Base):
    """Metric trace for Autonomous Microbial Electrogenic Biofilm Extracellular Electron Transfer (EET) Simulator."""

    __tablename__ = "p437_microbial_electrogenic_biofilm_flux_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p437_microbial_electrogenic_biofilm_flux_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MicrobialElectrogenicBiofilmStudy", back_populates="metric_traces")
