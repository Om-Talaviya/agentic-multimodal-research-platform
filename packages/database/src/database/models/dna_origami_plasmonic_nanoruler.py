"""SQLAlchemy models for Phase 506: Autonomous DNA Origami Reconfigurable Plasmonic Nanoruler Distance Calibrator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class DnaOrigamiPlasmonicNanorulerStudy(Base):
    """Study record for Autonomous DNA Origami Reconfigurable Plasmonic Nanoruler Distance Calibrator."""

    __tablename__ = "p506_dna_origami_plasmonic_nanoruler_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Scaffolded DNA Origami 12-Helix Bundle with Gold Nanoparticle Dimer Heterostructure")
    analytical_modality = Column(String(100), nullable=False, default="dna-origami-plasmonic-nanoruler")
    plasmonic_coupling_resonance_wavelength_nm = Column(Float, nullable=False, default=648.5)
    interparticle_gap_distance_nm = Column(Float, nullable=False, default=3.4)
    single_molecule_fluorescence_enhancement_factor = Column(Float, nullable=False, default=128.0)
    conformational_nanoruler_accuracy_pm = Column(Float, nullable=False, default=45.0)
    confidence_score = Column(Float, nullable=False, default=0.995)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("DnaOrigamiPlasmonicNanorulerItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("DnaOrigamiPlasmonicNanorulerMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class DnaOrigamiPlasmonicNanorulerItemProfile(Base):
    """Detailed item profile for Autonomous DNA Origami Reconfigurable Plasmonic Nanoruler Distance Calibrator."""

    __tablename__ = "p506_dna_origami_plasmonic_nanoruler_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p506_dna_origami_plasmonic_nanoruler_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DnaOrigamiPlasmonicNanorulerStudy", back_populates="item_profiles")


class DnaOrigamiPlasmonicNanorulerMetricTrace(Base):
    """Metric trace for Autonomous DNA Origami Reconfigurable Plasmonic Nanoruler Distance Calibrator."""

    __tablename__ = "p506_dna_origami_plasmonic_nanoruler_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p506_dna_origami_plasmonic_nanoruler_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DnaOrigamiPlasmonicNanorulerStudy", back_populates="metric_traces")
