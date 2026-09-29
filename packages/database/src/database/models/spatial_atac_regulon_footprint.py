"""SQLAlchemy models for Phase 362: Autonomous In Situ Spatial ATAC-seq Nuclear Transcription Factor Regulon Binding Footprinter."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SpatialAtacRegulonFootprintStudy(Base):
    """Study record for Reconstructs microfluidic barcode-indexed spatial open chromatin profiles at 20um pixel resolution to map pioneer transcription factor (e.g. FOXA1, SOX2, OCT4) digital genomic footprints across tissue sections.."""

    __tablename__ = "p362_sp_atac_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="spatial-atac-regulon-footprint")
    transcription_factor_footprint_flanking_depth_ratio = Column(Float, nullable=False, default=3.85)
    spatial_regulon_tissue_mapping_concordance_pct = Column(Float, nullable=False, default=97.4)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SpatialAtacRegulonFootprintItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("SpatialAtacRegulonFootprintMetricTrace", back_populates="study", cascade="all, delete-orphan")


class SpatialAtacRegulonFootprintItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "p362_sp_atac_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p362_sp_atac_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SpatialAtacRegulonFootprintStudy", back_populates="item_profiles")


class SpatialAtacRegulonFootprintMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "p362_sp_atac_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p362_sp_atac_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SpatialAtacRegulonFootprintStudy", back_populates="metric_traces")
