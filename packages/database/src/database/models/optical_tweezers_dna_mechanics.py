"""SQLAlchemy models for Phase 416: Autonomous Optical Tweezers DNA-Protein Mechanical Tension & Force-Extension Overstretching Modeler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class OpticalTweezersDnaMechanicsStudy(Base):
    """Study record for Autonomous Optical Tweezers DNA-Protein Mechanical Tension & Force-Extension Overstretching Modeler."""

    __tablename__ = "p416_optical_tweezers_dna_mechanics_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Single-Molecule Lambda-DNA Tether with RecA Nucleoprotein")
    analytical_modality = Column(String(100), nullable=False, default="optical-tweezers")
    overstretching_transition_force_pN = Column(Float, nullable=False, default=65.4)
    persistence_length_nm = Column(Float, nullable=False, default=47.8)
    contour_length_um = Column(Float, nullable=False, default=16.2)
    trap_stiffness_pN_per_nm = Column(Float, nullable=False, default=0.185)
    confidence_score = Column(Float, nullable=False, default=0.991)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("OpticalTweezersDnaMechanicsItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("OpticalTweezersDnaMechanicsMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class OpticalTweezersDnaMechanicsItemProfile(Base):
    """Detailed item profile for Autonomous Optical Tweezers DNA-Protein Mechanical Tension & Force-Extension Overstretching Modeler."""

    __tablename__ = "p416_optical_tweezers_dna_mechanics_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p416_optical_tweezers_dna_mechanics_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OpticalTweezersDnaMechanicsStudy", back_populates="item_profiles")


class OpticalTweezersDnaMechanicsMetricTrace(Base):
    """Metric trace for Autonomous Optical Tweezers DNA-Protein Mechanical Tension & Force-Extension Overstretching Modeler."""

    __tablename__ = "p416_optical_tweezers_dna_mechanics_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p416_optical_tweezers_dna_mechanics_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OpticalTweezersDnaMechanicsStudy", back_populates="metric_traces")
