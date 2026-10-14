"""SQLAlchemy models for Phase 482: Autonomous Cellular Ferroptosis Lipid Peroxidation Fenton Reaction Cascade Simulator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class FerroptosisFentonCascadeSimulatorStudy(Base):
    """Study record for Autonomous Cellular Ferroptosis Lipid Peroxidation Fenton Reaction Cascade Simulator."""

    __tablename__ = "p482_ferroptosis_fenton_cascade_simulator_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="GPX4-Inactivated HT-1080 Fibrosarcoma Spheroids with Labile Iron Pool Fe(II) Accumulation")
    analytical_modality = Column(String(100), nullable=False, default="ferroptosis-fenton-cascade")
    lipid_hydroperoxide_accumulation_nmol_mg = Column(Float, nullable=False, default=34.2)
    labile_iron_pool_chelatable_uM = Column(Float, nullable=False, default=8.45)
    fenton_reaction_rate_constant_M_inv_s_inv = Column(Float, nullable=False, default=76.0)
    membrane_permeabilization_lysis_probability = Column(Float, nullable=False, default=0.945)
    confidence_score = Column(Float, nullable=False, default=0.99)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("FerroptosisFentonCascadeSimulatorItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("FerroptosisFentonCascadeSimulatorMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class FerroptosisFentonCascadeSimulatorItemProfile(Base):
    """Detailed item profile for Autonomous Cellular Ferroptosis Lipid Peroxidation Fenton Reaction Cascade Simulator."""

    __tablename__ = "p482_ferroptosis_fenton_cascade_simulator_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p482_ferroptosis_fenton_cascade_simulator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("FerroptosisFentonCascadeSimulatorStudy", back_populates="item_profiles")


class FerroptosisFentonCascadeSimulatorMetricTrace(Base):
    """Metric trace for Autonomous Cellular Ferroptosis Lipid Peroxidation Fenton Reaction Cascade Simulator."""

    __tablename__ = "p482_ferroptosis_fenton_cascade_simulator_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p482_ferroptosis_fenton_cascade_simulator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("FerroptosisFentonCascadeSimulatorStudy", back_populates="metric_traces")
