"""SQLAlchemy models for Phase 537: Autonomous Single-Molecule Magnetic Torque Tweezers (MTT) DNA Supercoiling & Twist Modeler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SingleMoleculeMagneticTorqueTweezerStudy(Base):
    """Study record for Autonomous Single-Molecule Magnetic Torque Tweezers (MTT) DNA Supercoiling & Twist Modeler."""

    __tablename__ = "p537_single_molecule_magnetic_torque_tweezer_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Tethered 10-kb Double-Stranded DNA Molecule with Cylindrical Magnetic Bead in Horizontal Torque Field")
    analytical_modality = Column(String(100), nullable=False, default="magnetic-torque-tweezers-supercoiling")
    torsional_persistence_length_nm = Column(Float, nullable=False, default=84.0)
    buckling_transition_critical_torque_pN_nm = Column(Float, nullable=False, default=28.5)
    plectoneme_supercoil_conformation_density = Column(Float, nullable=False, default=0.052)
    dna_twist_stretch_coupling_constant_pN = Column(Float, nullable=False, default=-95.0)
    confidence_score = Column(Float, nullable=False, default=0.996)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SingleMoleculeMagneticTorqueTweezerItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SingleMoleculeMagneticTorqueTweezerMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SingleMoleculeMagneticTorqueTweezerItemProfile(Base):
    """Detailed item profile for Autonomous Single-Molecule Magnetic Torque Tweezers (MTT) DNA Supercoiling & Twist Modeler."""

    __tablename__ = "p537_single_molecule_magnetic_torque_tweezer_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p537_single_molecule_magnetic_torque_tweezer_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SingleMoleculeMagneticTorqueTweezerStudy", back_populates="item_profiles")


class SingleMoleculeMagneticTorqueTweezerMetricTrace(Base):
    """Metric trace for Autonomous Single-Molecule Magnetic Torque Tweezers (MTT) DNA Supercoiling & Twist Modeler."""

    __tablename__ = "p537_single_molecule_magnetic_torque_tweezer_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p537_single_molecule_magnetic_torque_tweezer_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SingleMoleculeMagneticTorqueTweezerStudy", back_populates="metric_traces")
