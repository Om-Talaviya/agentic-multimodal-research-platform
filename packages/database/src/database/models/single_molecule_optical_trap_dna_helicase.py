"""SQLAlchemy models for Phase 512: Autonomous Single-Molecule Dual-Trap Optical Tweezers DNA Helicase Unwinding Stepper."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SingleMoleculeOpticalTrapDnaHelicaseStudy(Base):
    """Study record for Autonomous Single-Molecule Dual-Trap Optical Tweezers DNA Helicase Unwinding Stepper."""

    __tablename__ = "p512_single_molecule_optical_trap_dna_helicase_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Dual-Beam Optical Trap Tethered dsDNA Hairpin with Recombinant Human Bloom Syndrome Helicase")
    analytical_modality = Column(String(100), nullable=False, default="optical-trap-helicase-unwinding")
    helicase_stepping_velocity_bp_per_s = Column(Float, nullable=False, default=48.5)
    atp_fuel_efficiency_bp_per_atp = Column(Float, nullable=False, default=1.0)
    strand_unwinding_processivity_bp = Column(Float, nullable=False, default=1450.0)
    sub_nanometer_step_size_bp = Column(Float, nullable=False, default=1.0)
    confidence_score = Column(Float, nullable=False, default=0.996)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SingleMoleculeOpticalTrapDnaHelicaseItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SingleMoleculeOpticalTrapDnaHelicaseMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SingleMoleculeOpticalTrapDnaHelicaseItemProfile(Base):
    """Detailed item profile for Autonomous Single-Molecule Dual-Trap Optical Tweezers DNA Helicase Unwinding Stepper."""

    __tablename__ = "p512_single_molecule_optical_trap_dna_helicase_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p512_single_molecule_optical_trap_dna_helicase_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SingleMoleculeOpticalTrapDnaHelicaseStudy", back_populates="item_profiles")


class SingleMoleculeOpticalTrapDnaHelicaseMetricTrace(Base):
    """Metric trace for Autonomous Single-Molecule Dual-Trap Optical Tweezers DNA Helicase Unwinding Stepper."""

    __tablename__ = "p512_single_molecule_optical_trap_dna_helicase_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p512_single_molecule_optical_trap_dna_helicase_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SingleMoleculeOpticalTrapDnaHelicaseStudy", back_populates="metric_traces")
