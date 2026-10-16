"""SQLAlchemy models for Phase 559: Autonomous Biohybrid Microbial Fuel Cell Extracellular Electron Shuttle Redox Kinetics Simulator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class BiohybridMicrobialFuelCellRedoxStudy(Base):
    """Study record for Autonomous Biohybrid Microbial Fuel Cell Extracellular Electron Shuttle Redox Kinetics Simulator."""

    __tablename__ = "p559_biohybrid_microbial_fuel_cell_redox_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Shewanella oneidensis MR-1 living Biofilm grown on 3D Carbon Nanotube Anode with Riboflavin Redox Mediators")
    analytical_modality = Column(String(100), nullable=False, default="biohybrid-microbial-fuel-cell")
    anodic_current_density_ma_cm2 = Column(Float, nullable=False, default=14.8)
    extracellular_electron_transfer_rate_per_sec = Column(Float, nullable=False, default=820.0)
    cytochrome_mtrc_reduction_potential_mv = Column(Float, nullable=False, default=-140.0)
    fuel_cell_maximum_power_density_mw_m2 = Column(Float, nullable=False, default=2450.0)
    confidence_score = Column(Float, nullable=False, default=0.994)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("BiohybridMicrobialFuelCellRedoxItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("BiohybridMicrobialFuelCellRedoxMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class BiohybridMicrobialFuelCellRedoxItemProfile(Base):
    """Detailed item profile for Autonomous Biohybrid Microbial Fuel Cell Extracellular Electron Shuttle Redox Kinetics Simulator."""

    __tablename__ = "p559_biohybrid_microbial_fuel_cell_redox_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p559_biohybrid_microbial_fuel_cell_redox_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("BiohybridMicrobialFuelCellRedoxStudy", back_populates="item_profiles")


class BiohybridMicrobialFuelCellRedoxMetricTrace(Base):
    """Metric trace for Autonomous Biohybrid Microbial Fuel Cell Extracellular Electron Shuttle Redox Kinetics Simulator."""

    __tablename__ = "p559_biohybrid_microbial_fuel_cell_redox_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p559_biohybrid_microbial_fuel_cell_redox_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("BiohybridMicrobialFuelCellRedoxStudy", back_populates="metric_traces")
