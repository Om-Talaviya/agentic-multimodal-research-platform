"""SQLAlchemy models for Phase 576: Autonomous Single-Molecule smFRET High-Fidelity DNA Polymerase Mismatch Proofreading & Exonuclease Kinetic Tracker."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SingleMoleculeFretPolymeraseFidelityTrackerStudy(Base):
    """Study record for Autonomous Single-Molecule smFRET High-Fidelity DNA Polymerase Mismatch Proofreading & Exonuclease Kinetic Tracker."""

    __tablename__ = "p576_single_molecule_fret_polymerase_fidelity_tracker_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Dual Cy3/Cy5-Labeled Primer-Template DNA Bound to Thermus aquaticus Polymerase I Active/Exo Sites")
    analytical_modality = Column(String(100), nullable=False, default="smfret-polymerase-fidelity-kinetics")
    fret_efficiency_transition_delta = Column(Float, nullable=False, default=0.42)
    exonuclease_proofreading_dwell_time_ms = Column(Float, nullable=False, default=85.0)
    mismatch_discrimination_factor = Column(Float, nullable=False, default=340.0)
    polymerization_catalytic_rate_nt_s = Column(Float, nullable=False, default=65.0)
    confidence_score = Column(Float, nullable=False, default=0.997)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SingleMoleculeFretPolymeraseFidelityTrackerItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SingleMoleculeFretPolymeraseFidelityTrackerMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SingleMoleculeFretPolymeraseFidelityTrackerItemProfile(Base):
    """Detailed item profile for Autonomous Single-Molecule smFRET High-Fidelity DNA Polymerase Mismatch Proofreading & Exonuclease Kinetic Tracker."""

    __tablename__ = "p576_single_molecule_fret_polymerase_fidelity_tracker_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p576_single_molecule_fret_polymerase_fidelity_tracker_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SingleMoleculeFretPolymeraseFidelityTrackerStudy", back_populates="item_profiles")


class SingleMoleculeFretPolymeraseFidelityTrackerMetricTrace(Base):
    """Metric trace for Autonomous Single-Molecule smFRET High-Fidelity DNA Polymerase Mismatch Proofreading & Exonuclease Kinetic Tracker."""

    __tablename__ = "p576_single_molecule_fret_polymerase_fidelity_tracker_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p576_single_molecule_fret_polymerase_fidelity_tracker_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SingleMoleculeFretPolymeraseFidelityTrackerStudy", back_populates="metric_traces")
