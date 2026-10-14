"""SQLAlchemy models for Phase 523: Autonomous Autonomous DNA Nanomachine Cargo Transport Track Walker & Dynamic Shuttle."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SyntheticDnaNanomachineCargoShuttleStudy(Base):
    """Study record for Autonomous Autonomous DNA Nanomachine Cargo Transport Track Walker & Dynamic Shuttle."""

    __tablename__ = "p523_synthetic_dna_nanomachine_cargo_shuttle_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Scaffolded DNA Origami 2D Origami Track with Autonomous Kinesin-Mimic Fuel-Fueled DNA Bipedal Walker")
    analytical_modality = Column(String(100), nullable=False, default="dna-nanomachine-shuttle")
    walker_directional_velocity_nm_per_min = Column(Float, nullable=False, default=18.0)
    fuel_strand_consumption_efficiency = Column(Float, nullable=False, default=0.965)
    molecular_cargo_handover_fidelity_pct = Column(Float, nullable=False, default=98.4)
    continuous_processive_stepping_distance_nm = Column(Float, nullable=False, default=320.0)
    confidence_score = Column(Float, nullable=False, default=0.993)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SyntheticDnaNanomachineCargoShuttleItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SyntheticDnaNanomachineCargoShuttleMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SyntheticDnaNanomachineCargoShuttleItemProfile(Base):
    """Detailed item profile for Autonomous Autonomous DNA Nanomachine Cargo Transport Track Walker & Dynamic Shuttle."""

    __tablename__ = "p523_synthetic_dna_nanomachine_cargo_shuttle_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p523_synthetic_dna_nanomachine_cargo_shuttle_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SyntheticDnaNanomachineCargoShuttleStudy", back_populates="item_profiles")


class SyntheticDnaNanomachineCargoShuttleMetricTrace(Base):
    """Metric trace for Autonomous Autonomous DNA Nanomachine Cargo Transport Track Walker & Dynamic Shuttle."""

    __tablename__ = "p523_synthetic_dna_nanomachine_cargo_shuttle_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p523_synthetic_dna_nanomachine_cargo_shuttle_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SyntheticDnaNanomachineCargoShuttleStudy", back_populates="metric_traces")
