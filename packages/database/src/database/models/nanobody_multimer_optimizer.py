"""SQLAlchemy models for Phase 382: Autonomous Therapeutic Nanobody Multimerization & Valency Geometry Optimizer."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class NanobodyMultimerOptimizerStudy(Base):
    """Study record for Optimizes flexible (Gly4Ser)n peptide linker lengths and geometric orientations for biparatopic and multivalent single-domain VHH antibodies to induce targeted receptor clustering.."""

    __tablename__ = "p382_nanobody_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="nanobody-multimer-optimizer")
    multivalent_avidity_gain_fold = Column(Float, nullable=False, default=125.0)
    receptor_internalization_downregulation_pct = Column(Float, nullable=False, default=91.8)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("NanobodyMultimerOptimizerItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("NanobodyMultimerOptimizerMetricTrace", back_populates="study", cascade="all, delete-orphan")


class NanobodyMultimerOptimizerItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "p382_nanobody_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p382_nanobody_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NanobodyMultimerOptimizerStudy", back_populates="item_profiles")


class NanobodyMultimerOptimizerMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "p382_nanobody_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p382_nanobody_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NanobodyMultimerOptimizerStudy", back_populates="metric_traces")
