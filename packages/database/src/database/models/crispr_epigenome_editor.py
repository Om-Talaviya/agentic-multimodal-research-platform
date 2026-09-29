"""SQLAlchemy models for Phase 365: Autonomous Ultra-High Throughput CRISPR Epigenome Editing dCas9-DNMT3A/TET1 Methylation Writer/Eraser."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CrisprEpigenomeEditorStudy(Base):
    """Study record for Guides deactivated dCas9 conjugated with DNA methyltransferases (DNMT3A-3L) or demethylases (TET1 catalytic domain) to write or erase targeted CpG island methylation for durable gene repression/activation.."""

    __tablename__ = "p365_epi_edit_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="crispr-epigenome-editor")
    target_cpg_methylation_alteration_pct = Column(Float, nullable=False, default=91.5)
    epigenetic_silencing_durability_cell_divisions = Column(Float, nullable=False, default=45.0)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CrisprEpigenomeEditorItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("CrisprEpigenomeEditorMetricTrace", back_populates="study", cascade="all, delete-orphan")


class CrisprEpigenomeEditorItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "p365_epi_edit_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p365_epi_edit_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CrisprEpigenomeEditorStudy", back_populates="item_profiles")


class CrisprEpigenomeEditorMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "p365_epi_edit_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p365_epi_edit_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CrisprEpigenomeEditorStudy", back_populates="metric_traces")
