"""SQLAlchemy models for Phase 443: Autonomous Cellular Senescence-Associated Secretory Phenotype (SASP) Paracrine Spreading & Tissue Exhaustion Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CellularSenescenceSaspStudy(Base):
    """Study record for Autonomous Cellular Senescence-Associated Secretory Phenotype (SASP) Paracrine Spreading & Tissue Exhaustion Engine."""

    __tablename__ = "p443_cellular_senescence_sasp_paracrine_spreading_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Replicative Senescent Human Dermal Fibroblasts in 3D Collagen Microtissue with Bystander Cells")
    analytical_modality = Column(String(100), nullable=False, default="senescence-sasp-spreading")
    sasp_paracrine_diffusion_radius_um = Column(Float, nullable=False, default=185.0)
    p16_ink4a_induction_fold_change = Column(Float, nullable=False, default=5.85)
    bystander_senescence_induction_rate = Column(Float, nullable=False, default=0.385)
    senolytic_depletion_efficacy_score = Column(Float, nullable=False, default=0.942)
    confidence_score = Column(Float, nullable=False, default=0.99)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CellularSenescenceSaspItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("CellularSenescenceSaspMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class CellularSenescenceSaspItemProfile(Base):
    """Detailed item profile for Autonomous Cellular Senescence-Associated Secretory Phenotype (SASP) Paracrine Spreading & Tissue Exhaustion Engine."""

    __tablename__ = "p443_cellular_senescence_sasp_paracrine_spreading_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p443_cellular_senescence_sasp_paracrine_spreading_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CellularSenescenceSaspStudy", back_populates="item_profiles")


class CellularSenescenceSaspMetricTrace(Base):
    """Metric trace for Autonomous Cellular Senescence-Associated Secretory Phenotype (SASP) Paracrine Spreading & Tissue Exhaustion Engine."""

    __tablename__ = "p443_cellular_senescence_sasp_paracrine_spreading_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p443_cellular_senescence_sasp_paracrine_spreading_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CellularSenescenceSaspStudy", back_populates="metric_traces")
