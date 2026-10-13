"""SQLAlchemy models for Phase 460: Autonomous In-Situ Cryo-CLEM Fluorescent Target Correlation & Precision Fiducial Alignment Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CryoClemFiducialAlignmentStudy(Base):
    """Study record for Autonomous In-Situ Cryo-CLEM Fluorescent Target Correlation & Precision Fiducial Alignment Engine."""

    __tablename__ = "p460_cryo_clem_fiducial_alignment_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Vitrified Primary Axon Growth Cone with Gold Nanoparticle Fiducials and GFP-Tagged Cargo")
    analytical_modality = Column(String(100), nullable=False, default="cryo-clem-fiducial-alignment")
    coordinate_transformation_target_registration_error_nm = Column(Float, nullable=False, default=28.5)
    fiducial_triangulation_residual_angstrom = Column(Float, nullable=False, default=18.2)
    fluorescence_cryo_snr_decibels = Column(Float, nullable=False, default=24.6)
    target_feature_hit_probability = Column(Float, nullable=False, default=0.965)
    confidence_score = Column(Float, nullable=False, default=0.993)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CryoClemFiducialAlignmentItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("CryoClemFiducialAlignmentMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class CryoClemFiducialAlignmentItemProfile(Base):
    """Detailed item profile for Autonomous In-Situ Cryo-CLEM Fluorescent Target Correlation & Precision Fiducial Alignment Engine."""

    __tablename__ = "p460_cryo_clem_fiducial_alignment_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p460_cryo_clem_fiducial_alignment_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CryoClemFiducialAlignmentStudy", back_populates="item_profiles")


class CryoClemFiducialAlignmentMetricTrace(Base):
    """Metric trace for Autonomous In-Situ Cryo-CLEM Fluorescent Target Correlation & Precision Fiducial Alignment Engine."""

    __tablename__ = "p460_cryo_clem_fiducial_alignment_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p460_cryo_clem_fiducial_alignment_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CryoClemFiducialAlignmentStudy", back_populates="metric_traces")
