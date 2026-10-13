"""SQLAlchemy models for Phase 465: Autonomous Microfluidic Acoustic Tweezers Multicellular Spheroid Patterning & Cytoskeletal Stress Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class AcousticTweezersSpheroidPatterningStudy(Base):
    """Study record for Autonomous Microfluidic Acoustic Tweezers Multicellular Spheroid Patterning & Cytoskeletal Stress Engine."""

    __tablename__ = "p465_acoustic_tweezers_spheroid_patterning_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="3D MCF-7 Breast Tumor Spheroid Array patterned in 2.5 MHz Standing Bulk Acoustic Wave Resonator")
    analytical_modality = Column(String(100), nullable=False, default="acoustic-spheroid-patterning")
    acoustic_radiation_force_pN = Column(Float, nullable=False, default=42.5)
    spheroid_diameter_uniformity_cv = Column(Float, nullable=False, default=0.048)
    cytoskeletal_f_actin_alignment_index = Column(Float, nullable=False, default=0.885)
    acoustic_trapping_node_stability = Column(Float, nullable=False, default=0.992)
    confidence_score = Column(Float, nullable=False, default=0.991)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("AcousticTweezersSpheroidPatterningItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("AcousticTweezersSpheroidPatterningMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class AcousticTweezersSpheroidPatterningItemProfile(Base):
    """Detailed item profile for Autonomous Microfluidic Acoustic Tweezers Multicellular Spheroid Patterning & Cytoskeletal Stress Engine."""

    __tablename__ = "p465_acoustic_tweezers_spheroid_patterning_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p465_acoustic_tweezers_spheroid_patterning_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("AcousticTweezersSpheroidPatterningStudy", back_populates="item_profiles")


class AcousticTweezersSpheroidPatterningMetricTrace(Base):
    """Metric trace for Autonomous Microfluidic Acoustic Tweezers Multicellular Spheroid Patterning & Cytoskeletal Stress Engine."""

    __tablename__ = "p465_acoustic_tweezers_spheroid_patterning_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p465_acoustic_tweezers_spheroid_patterning_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("AcousticTweezersSpheroidPatterningStudy", back_populates="metric_traces")
