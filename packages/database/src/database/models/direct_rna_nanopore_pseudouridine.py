"""SQLAlchemy models for Phase 415: Autonomous Epitranscriptomic Direct RNA Nanopore Pseudouridine (Psi) & m6A Stoichiometry Profiler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class DirectRnaNanoporePseudouridineStudy(Base):
    """Study record for Autonomous Epitranscriptomic Direct RNA Nanopore Pseudouridine (Psi) & m6A Stoichiometry Profiler."""

    __tablename__ = "p415_direct_rna_nanopore_pseudouridine_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Cellular Poly(A)+ Native mRNA Transcriptome")
    analytical_modality = Column(String(100), nullable=False, default="direct-rna-nanopore")
    pseudouridine_stoichiometry_ratio = Column(Float, nullable=False, default=0.842)
    nanopore_dwell_time_shift_ms = Column(Float, nullable=False, default=14.8)
    ionic_current_deviation_pA = Column(Float, nullable=False, default=6.2)
    m6a_modification_frequency = Column(Float, nullable=False, default=0.765)
    confidence_score = Column(Float, nullable=False, default=0.987)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("DirectRnaNanoporePseudouridineItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("DirectRnaNanoporePseudouridineMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class DirectRnaNanoporePseudouridineItemProfile(Base):
    """Detailed item profile for Autonomous Epitranscriptomic Direct RNA Nanopore Pseudouridine (Psi) & m6A Stoichiometry Profiler."""

    __tablename__ = "p415_direct_rna_nanopore_pseudouridine_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p415_direct_rna_nanopore_pseudouridine_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DirectRnaNanoporePseudouridineStudy", back_populates="item_profiles")


class DirectRnaNanoporePseudouridineMetricTrace(Base):
    """Metric trace for Autonomous Epitranscriptomic Direct RNA Nanopore Pseudouridine (Psi) & m6A Stoichiometry Profiler."""

    __tablename__ = "p415_direct_rna_nanopore_pseudouridine_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p415_direct_rna_nanopore_pseudouridine_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DirectRnaNanoporePseudouridineStudy", back_populates="metric_traces")
