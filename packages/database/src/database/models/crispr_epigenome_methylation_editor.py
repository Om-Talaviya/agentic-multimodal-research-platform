"""SQLAlchemy models for Phase 256: Autonomous Targeted CRISPR Epigenome Methylation/Demethylation Editing & Chromatin Accessibility Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CrisprEpigenomeMethylationEditorStudy(Base):
    """Study record for Models locus-specific targeted DNA methylation and demethylation using dCas9-DNMT3A and dCas9-TET1 fusions, predicting chromatin accessibility transitions and transcriptional persistence.."""

    __tablename__ = "crispr_epigenome_edit_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="crispr-epigenome-methylation-editor")
    cpg_methylation_efficiency_pct = Column(Float, nullable=False, default=89.2)
    chromatin_accessibility_fold_change = Column(Float, nullable=False, default=5.4)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CrisprEpigenomeMethylationEditorItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("CrisprEpigenomeMethylationEditorMetricTrace", back_populates="study", cascade="all, delete-orphan")


class CrisprEpigenomeMethylationEditorItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "crispr_epigenome_edit_item_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("crispr_epigenome_edit_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CrisprEpigenomeMethylationEditorStudy", back_populates="item_profiles")


class CrisprEpigenomeMethylationEditorMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "crispr_epigenome_edit_metric_traces"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("crispr_epigenome_edit_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CrisprEpigenomeMethylationEditorStudy", back_populates="metric_traces")
