"""SQLAlchemy models for Phase 388: Autonomous High-Content Organoid Electrophysiology Micro-Capillary Patch-Clamp Analyzer."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class OrganoidPatchClampAnalyzerStudy(Base):
    """Study record for Automates gigaseal formation detection, whole-cell capacitance cancellation, series resistance compensation, and Hodgkin-Huxley voltage-gated Na+/K+ ion channel kinetic parameter fitting.."""

    __tablename__ = "p388_patch_clamp_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="organoid-patch-clamp-analyzer")
    action_potential_amplitude_millivolts = Column(Float, nullable=False, default=95.0)
    whole_cell_gigaseal_formation_success_pct = Column(Float, nullable=False, default=92.5)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("OrganoidPatchClampAnalyzerItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("OrganoidPatchClampAnalyzerMetricTrace", back_populates="study", cascade="all, delete-orphan")


class OrganoidPatchClampAnalyzerItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "p388_patch_clamp_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p388_patch_clamp_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OrganoidPatchClampAnalyzerStudy", back_populates="item_profiles")


class OrganoidPatchClampAnalyzerMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "p388_patch_clamp_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p388_patch_clamp_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OrganoidPatchClampAnalyzerStudy", back_populates="metric_traces")
