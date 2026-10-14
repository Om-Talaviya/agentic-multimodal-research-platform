"""SQLAlchemy models for Phase 503: Autonomous Synthetic Protocellular Compartment Membraneless Coacervate-GUV Hybrid Bionanoreactor."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CoacervateGuvHybridBionanoreactorStudy(Base):
    """Study record for Autonomous Synthetic Protocellular Compartment Membraneless Coacervate-GUV Hybrid Bionanoreactor."""

    __tablename__ = "p503_coacervate_guv_hybrid_bionanoreactor_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Liquid-Liquid Phase Separated Polylysine-ATP Coacervates Encapsulated within POPC/Cholesterol Bilayer GUVs")
    analytical_modality = Column(String(100), nullable=False, default="coacervate-guv-hybrid-reactor")
    enzyme_partition_coefficient_k_partition = Column(Float, nullable=False, default=38.5)
    internal_substrate_conversion_flux_uM_per_s = Column(Float, nullable=False, default=12.8)
    membrane_selective_permeation_pore_cutoff_kDa = Column(Float, nullable=False, default=4.5)
    coacervate_droplet_stability_retention_days = Column(Float, nullable=False, default=14.0)
    confidence_score = Column(Float, nullable=False, default=0.993)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CoacervateGuvHybridBionanoreactorItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("CoacervateGuvHybridBionanoreactorMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class CoacervateGuvHybridBionanoreactorItemProfile(Base):
    """Detailed item profile for Autonomous Synthetic Protocellular Compartment Membraneless Coacervate-GUV Hybrid Bionanoreactor."""

    __tablename__ = "p503_coacervate_guv_hybrid_bionanoreactor_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p503_coacervate_guv_hybrid_bionanoreactor_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CoacervateGuvHybridBionanoreactorStudy", back_populates="item_profiles")


class CoacervateGuvHybridBionanoreactorMetricTrace(Base):
    """Metric trace for Autonomous Synthetic Protocellular Compartment Membraneless Coacervate-GUV Hybrid Bionanoreactor."""

    __tablename__ = "p503_coacervate_guv_hybrid_bionanoreactor_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p503_coacervate_guv_hybrid_bionanoreactor_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CoacervateGuvHybridBionanoreactorStudy", back_populates="metric_traces")
