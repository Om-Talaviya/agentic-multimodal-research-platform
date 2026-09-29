"""SQLAlchemy models for Phase 282: Autonomous Single-Cell Chromatin Conformation (scHi-C) 3D Loop & Topologically Associating Domain Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SingleCellHic3dChromatinLoopStudy(Base):
    """Study record for Reconstructs single-cell 3D chromatin conformation maps from sparse scHi-C contacts, decompacting cell-to-cell TAD boundary variance and enhancer-promoter loops.."""

    __tablename__ = "sc_hic_3d_chromatin_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="single-cell-hic-3d-chromatin-loop")
    single_cell_tad_boundary_precision_score = Column(Float, nullable=False, default=95.6)
    chromatin_loop_contact_enrichment_fold = Column(Float, nullable=False, default=7.4)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SingleCellHic3dChromatinLoopItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("SingleCellHic3dChromatinLoopMetricTrace", back_populates="study", cascade="all, delete-orphan")


class SingleCellHic3dChromatinLoopItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "sc_hic_3d_chromatin_item_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("sc_hic_3d_chromatin_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SingleCellHic3dChromatinLoopStudy", back_populates="item_profiles")


class SingleCellHic3dChromatinLoopMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "sc_hic_3d_chromatin_metric_traces"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("sc_hic_3d_chromatin_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SingleCellHic3dChromatinLoopStudy", back_populates="metric_traces")
