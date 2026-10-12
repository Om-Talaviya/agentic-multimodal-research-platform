"""SQLAlchemy models for Phase 417: Autonomous Solid-State Silicon Nitride Nanopore Single-Molecule Protein Translocation Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SolidStateNanoporeSensingStudy(Base):
    """Study record for Autonomous Solid-State Silicon Nitride Nanopore Single-Molecule Protein Translocation Engine."""

    __tablename__ = "p417_solid_state_nanopore_single_molecule_sensing_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Conformationally Stretched Native Protein Translocation Through Sub-5nm SiNx Nanopore")
    analytical_modality = Column(String(100), nullable=False, default="solid-state-nanopore")
    translocation_dwell_time_us = Column(Float, nullable=False, default=245.0)
    fractional_current_blockade_ratio = Column(Float, nullable=False, default=0.785)
    nanopore_diameter_nm = Column(Float, nullable=False, default=3.8)
    capture_frequency_events_per_s = Column(Float, nullable=False, default=18.5)
    confidence_score = Column(Float, nullable=False, default=0.988)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SolidStateNanoporeSensingItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SolidStateNanoporeSensingMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SolidStateNanoporeSensingItemProfile(Base):
    """Detailed item profile for Autonomous Solid-State Silicon Nitride Nanopore Single-Molecule Protein Translocation Engine."""

    __tablename__ = "p417_solid_state_nanopore_single_molecule_sensing_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p417_solid_state_nanopore_single_molecule_sensing_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SolidStateNanoporeSensingStudy", back_populates="item_profiles")


class SolidStateNanoporeSensingMetricTrace(Base):
    """Metric trace for Autonomous Solid-State Silicon Nitride Nanopore Single-Molecule Protein Translocation Engine."""

    __tablename__ = "p417_solid_state_nanopore_single_molecule_sensing_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p417_solid_state_nanopore_single_molecule_sensing_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SolidStateNanoporeSensingStudy", back_populates="metric_traces")
