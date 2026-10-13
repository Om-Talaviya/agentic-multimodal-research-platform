"""SQLAlchemy models for Phase 451: Autonomous Single-Molecule Optical Tweezers Ribosome Translation Kinetic Polypeptide Translocation Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class OpticalTweezersRibosomeTranslationStudy(Base):
    """Study record for Autonomous Single-Molecule Optical Tweezers Ribosome Translation Kinetic Polypeptide Translocation Engine."""

    __tablename__ = "p451_optical_tweezers_ribosome_translation_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="70S Bacterial Ribosome Translating Structured mRNA Stem-Loop under Constant Force (12 pN)")
    analytical_modality = Column(String(100), nullable=False, default="ribosome-translation-dynamics")
    codon_stepping_dwell_time_ms = Column(Float, nullable=False, default=68.4)
    mrna_unfolding_barrier_activation_energy_kb_t = Column(Float, nullable=False, default=14.8)
    frameshift_slippage_probability = Column(Float, nullable=False, default=0.0035)
    elongation_rate_amino_acids_per_s = Column(Float, nullable=False, default=14.6)
    confidence_score = Column(Float, nullable=False, default=0.994)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("OpticalTweezersRibosomeTranslationItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("OpticalTweezersRibosomeTranslationMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class OpticalTweezersRibosomeTranslationItemProfile(Base):
    """Detailed item profile for Autonomous Single-Molecule Optical Tweezers Ribosome Translation Kinetic Polypeptide Translocation Engine."""

    __tablename__ = "p451_optical_tweezers_ribosome_translation_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p451_optical_tweezers_ribosome_translation_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OpticalTweezersRibosomeTranslationStudy", back_populates="item_profiles")


class OpticalTweezersRibosomeTranslationMetricTrace(Base):
    """Metric trace for Autonomous Single-Molecule Optical Tweezers Ribosome Translation Kinetic Polypeptide Translocation Engine."""

    __tablename__ = "p451_optical_tweezers_ribosome_translation_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p451_optical_tweezers_ribosome_translation_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OpticalTweezersRibosomeTranslationStudy", back_populates="metric_traces")
