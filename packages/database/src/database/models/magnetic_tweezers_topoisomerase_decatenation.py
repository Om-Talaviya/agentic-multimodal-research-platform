"""SQLAlchemy models for Phase 484: Autonomous Single-Molecule Magnetic Tweezers Topoisomerase Type II DNA Catenation Decatenator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MagneticTweezersTopoisomeraseDecatenationStudy(Base):
    """Study record for Autonomous Single-Molecule Magnetic Tweezers Topoisomerase Type II DNA Catenation Decatenator."""

    __tablename__ = "p484_magnetic_tweezers_topoisomerase_decatenation_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Tethered Braided DNA Minicircle Pair with Purified Human Topoisomerase II-alpha in Flow Cell")
    analytical_modality = Column(String(100), nullable=False, default="magnetic-tweezers-decatenation")
    decatenation_catalytic_rate_per_sec = Column(Float, nullable=False, default=3.85)
    atp_hydrolysis_coupling_ratio = Column(Float, nullable=False, default=1.98)
    t_segment_strand_passage_dwell_time_ms = Column(Float, nullable=False, default=145.0)
    supercoiling_linking_number_delta = Column(Float, nullable=False, default=-2.0)
    confidence_score = Column(Float, nullable=False, default=0.992)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MagneticTweezersTopoisomeraseDecatenationItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MagneticTweezersTopoisomeraseDecatenationMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MagneticTweezersTopoisomeraseDecatenationItemProfile(Base):
    """Detailed item profile for Autonomous Single-Molecule Magnetic Tweezers Topoisomerase Type II DNA Catenation Decatenator."""

    __tablename__ = "p484_magnetic_tweezers_topoisomerase_decatenation_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p484_magnetic_tweezers_topoisomerase_decatenation_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MagneticTweezersTopoisomeraseDecatenationStudy", back_populates="item_profiles")


class MagneticTweezersTopoisomeraseDecatenationMetricTrace(Base):
    """Metric trace for Autonomous Single-Molecule Magnetic Tweezers Topoisomerase Type II DNA Catenation Decatenator."""

    __tablename__ = "p484_magnetic_tweezers_topoisomerase_decatenation_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p484_magnetic_tweezers_topoisomerase_decatenation_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MagneticTweezersTopoisomeraseDecatenationStudy", back_populates="metric_traces")
