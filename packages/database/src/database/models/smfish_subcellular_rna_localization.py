"""SQLAlchemy models for Phase 253: Autonomous Single-Molecule FISH Subcellular RNA Transcript Localization & Cluster Analysis Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SmfishSubcellularRnaLocalizationStudy(Base):
    """Study record for Quantifies subcellular single-molecule RNA spot distributions via 3D point spread function fitting, calculating Ripley's K clustering and perinuclear-to-cytoplasmic enrichment ratios.."""

    __tablename__ = "smfish_rna_loc_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="smfish-subcellular-rna-localization")
    psf_localization_precision_nm = Column(Float, nullable=False, default=12.4)
    subcellular_clustering_ripleys_k_score = Column(Float, nullable=False, default=3.6)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SmfishSubcellularRnaLocalizationItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("SmfishSubcellularRnaLocalizationMetricTrace", back_populates="study", cascade="all, delete-orphan")


class SmfishSubcellularRnaLocalizationItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "smfish_rna_loc_item_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("smfish_rna_loc_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SmfishSubcellularRnaLocalizationStudy", back_populates="item_profiles")


class SmfishSubcellularRnaLocalizationMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "smfish_rna_loc_metric_traces"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("smfish_rna_loc_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SmfishSubcellularRnaLocalizationStudy", back_populates="metric_traces")
