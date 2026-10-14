"""SQLAlchemy models for Phase 520: Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy Protein Nucleation Real-Time Tracker."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class LiquidCellTemProteinCrystallizationStudy(Base):
    """Study record for Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy Protein Nucleation Real-Time Tracker."""

    __tablename__ = "p520_liquid_cell_tem_protein_crystallization_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Silicon Nitride Microchip Graphene Liquid Cell with Supersaturated Hen Egg-White Lysozyme Solution")
    analytical_modality = Column(String(100), nullable=False, default="liquid-cell-tem-crystallization")
    critical_nucleus_radius_nm = Column(Float, nullable=False, default=2.4)
    non_classical_pre_nucleation_cluster_density_per_um3 = Column(Float, nullable=False, default=1250.0)
    crystal_facet_growth_rate_nm_per_min = Column(Float, nullable=False, default=1.85)
    electron_beam_dose_induced_radiolysis_damage_threshold_e_per_angstrom2 = Column(Float, nullable=False, default=2.5)
    confidence_score = Column(Float, nullable=False, default=0.994)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("LiquidCellTemProteinCrystallizationItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("LiquidCellTemProteinCrystallizationMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class LiquidCellTemProteinCrystallizationItemProfile(Base):
    """Detailed item profile for Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy Protein Nucleation Real-Time Tracker."""

    __tablename__ = "p520_liquid_cell_tem_protein_crystallization_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p520_liquid_cell_tem_protein_crystallization_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("LiquidCellTemProteinCrystallizationStudy", back_populates="item_profiles")


class LiquidCellTemProteinCrystallizationMetricTrace(Base):
    """Metric trace for Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy Protein Nucleation Real-Time Tracker."""

    __tablename__ = "p520_liquid_cell_tem_protein_crystallization_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p520_liquid_cell_tem_protein_crystallization_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("LiquidCellTemProteinCrystallizationStudy", back_populates="metric_traces")
