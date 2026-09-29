"""SQLAlchemy models for Phase 307: Autonomous Spatial Proteomics Imaging Mass Cytometry (IMC) Single-Cell Neighborhood Interaction & Escape Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class ImcSpatialProteomicsNeighborhoodStudy(Base):
    """Study record for Analyzes 40-plex metal-tagged imaging mass cytometry sections, mapping cellular neighborhood adjacency graphs and quantifying tumor-immune spatial evasion.."""

    __tablename__ = "imc_neighborhood_escape_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="imc-spatial-proteomics-neighborhood")
    cellular_neighborhood_classification_f1_score = Column(Float, nullable=False, default=96.8)
    tumor_immune_spatial_evasion_score = Column(Float, nullable=False, default=3.8)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("ImcSpatialProteomicsNeighborhoodItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("ImcSpatialProteomicsNeighborhoodMetricTrace", back_populates="study", cascade="all, delete-orphan")


class ImcSpatialProteomicsNeighborhoodItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "imc_neighborhood_escape_item_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("imc_neighborhood_escape_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("ImcSpatialProteomicsNeighborhoodStudy", back_populates="item_profiles")


class ImcSpatialProteomicsNeighborhoodMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "imc_neighborhood_escape_metric_traces"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("imc_neighborhood_escape_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("ImcSpatialProteomicsNeighborhoodStudy", back_populates="metric_traces")
