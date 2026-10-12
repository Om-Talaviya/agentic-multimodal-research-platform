"""SQLAlchemy models for Phase 428: Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy (LC-TEM) Nanoparticle Nucleation Simulator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class LiquidCellTemNucleationStudy(Base):
    """Study record for Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy (LC-TEM) Nanoparticle Nucleation Simulator."""

    __tablename__ = "p428_liquid_cell_tem_nucleation_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Silicon Nitride Liquid Cell with Gold Nanocrystal Growth Solution")
    analytical_modality = Column(String(100), nullable=False, default="liquid-cell-tem")
    nucleation_rate_particles_per_s_um2 = Column(Float, nullable=False, default=14.2)
    critical_nucleus_radius_nm = Column(Float, nullable=False, default=1.45)
    non_classical_attachment_frequency = Column(Float, nullable=False, default=0.785)
    electron_beam_dose_rate_e_per_ang2_s = Column(Float, nullable=False, default=8.5)
    confidence_score = Column(Float, nullable=False, default=0.984)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("LiquidCellTemNucleationItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("LiquidCellTemNucleationMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class LiquidCellTemNucleationItemProfile(Base):
    """Detailed item profile for Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy (LC-TEM) Nanoparticle Nucleation Simulator."""

    __tablename__ = "p428_liquid_cell_tem_nucleation_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p428_liquid_cell_tem_nucleation_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("LiquidCellTemNucleationStudy", back_populates="item_profiles")


class LiquidCellTemNucleationMetricTrace(Base):
    """Metric trace for Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy (LC-TEM) Nanoparticle Nucleation Simulator."""

    __tablename__ = "p428_liquid_cell_tem_nucleation_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p428_liquid_cell_tem_nucleation_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("LiquidCellTemNucleationStudy", back_populates="metric_traces")
