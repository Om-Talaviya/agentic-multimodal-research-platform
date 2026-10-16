"""SQLAlchemy models for Phase 558: Autonomous Single-Molecule Mechanical Force Spectroscopy Chromatin Fiber Nucleosome Unwrapping Modeler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SingleMoleculeChromatinNucleosomeUnwrappingStudy(Base):
    """Study record for Autonomous Single-Molecule Mechanical Force Spectroscopy Chromatin Fiber Nucleosome Unwrapping Modeler."""

    __tablename__ = "p558_single_molecule_chromatin_nucleosome_unwrapping_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Reconstituted 12-Nucleosome Chromatin Array with Widom 601 positioning sequences stretched via Dual-Beam Optical Tweezers")
    analytical_modality = Column(String(100), nullable=False, default="chromatin-force-spectroscopy")
    outer_turn_unwrapping_force_threshold_pn = Column(Float, nullable=False, default=3.8)
    inner_turn_cooperative_rupture_force_pn = Column(Float, nullable=False, default=15.2)
    histone_octamer_dissociation_work_kcal_mol = Column(Float, nullable=False, default=26.4)
    unwrapped_dna_contour_length_release_nm = Column(Float, nullable=False, default=52.0)
    confidence_score = Column(Float, nullable=False, default=0.996)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SingleMoleculeChromatinNucleosomeUnwrappingItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SingleMoleculeChromatinNucleosomeUnwrappingMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SingleMoleculeChromatinNucleosomeUnwrappingItemProfile(Base):
    """Detailed item profile for Autonomous Single-Molecule Mechanical Force Spectroscopy Chromatin Fiber Nucleosome Unwrapping Modeler."""

    __tablename__ = "p558_single_molecule_chromatin_nucleosome_unwrapping_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p558_single_molecule_chromatin_nucleosome_unwrapping_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SingleMoleculeChromatinNucleosomeUnwrappingStudy", back_populates="item_profiles")


class SingleMoleculeChromatinNucleosomeUnwrappingMetricTrace(Base):
    """Metric trace for Autonomous Single-Molecule Mechanical Force Spectroscopy Chromatin Fiber Nucleosome Unwrapping Modeler."""

    __tablename__ = "p558_single_molecule_chromatin_nucleosome_unwrapping_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p558_single_molecule_chromatin_nucleosome_unwrapping_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SingleMoleculeChromatinNucleosomeUnwrappingStudy", back_populates="metric_traces")
