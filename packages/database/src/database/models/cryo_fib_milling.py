"""SQLAlchemy models for Phase 414: Autonomous Cryo-FIB Milling & In-Situ Lamella Thickness Optimization Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CryoFibMillingStudy(Base):
    """Study record for Autonomous Cryo-FIB Milling & In-Situ Lamella Thickness Optimization Engine."""

    __tablename__ = "p414_cryo_fib_milling_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Vitreous Cellular Cryo-Lamella")
    analytical_modality = Column(String(100), nullable=False, default="cryo-fib-milling")
    in_situ_lamella_thickness_nm = Column(Float, nullable=False, default=112.5)
    curtaining_artifact_suppression_ratio = Column(Float, nullable=False, default=0.948)
    gallium_ion_beam_current_pA = Column(Float, nullable=False, default=30.0)
    vitreous_ice_preservation_score = Column(Float, nullable=False, default=0.982)
    confidence_score = Column(Float, nullable=False, default=0.988)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CryoFibMillingItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("CryoFibMillingMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class CryoFibMillingItemProfile(Base):
    """Detailed item profile for Cryo-FIB milling step/site."""

    __tablename__ = "p414_cryo_fib_milling_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p414_cryo_fib_milling_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Milling Stage")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CryoFibMillingStudy", back_populates="item_profiles")


class CryoFibMillingMetricTrace(Base):
    """Longitudinal and dimensional metric trace for thickness and beam dynamics."""

    __tablename__ = "p414_cryo_fib_milling_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p414_cryo_fib_milling_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CryoFibMillingStudy", back_populates="metric_traces")
