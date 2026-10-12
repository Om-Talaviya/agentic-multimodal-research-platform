"""SQLAlchemy models for Phase 422: Autonomous Allosteric Ligand Residence Time & Dissociation Rate Constant (k_off) Molecular Dynamics Extractor."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class LigandResidenceTimeKoffStudy(Base):
    """Study record for Autonomous Allosteric Ligand Residence Time & Dissociation Rate Constant (k_off) Molecular Dynamics Extractor."""

    __tablename__ = "p422_ligand_residence_time_koff_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Kinase Allosteric Pocket with Type II Small Molecule Inhibitor")
    analytical_modality = Column(String(100), nullable=False, default="residence-time-koff")
    unbinding_rate_koff_s_inv = Column(Float, nullable=False, default=0.0024)
    residence_time_minutes = Column(Float, nullable=False, default=416.7)
    dissociation_free_energy_barrier_kcal = Column(Float, nullable=False, default=21.4)
    binding_pocket_hydration_entropy = Column(Float, nullable=False, default=-8.6)
    confidence_score = Column(Float, nullable=False, default=0.984)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("LigandResidenceTimeKoffItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("LigandResidenceTimeKoffMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class LigandResidenceTimeKoffItemProfile(Base):
    """Detailed item profile for Autonomous Allosteric Ligand Residence Time & Dissociation Rate Constant (k_off) Molecular Dynamics Extractor."""

    __tablename__ = "p422_ligand_residence_time_koff_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p422_ligand_residence_time_koff_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("LigandResidenceTimeKoffStudy", back_populates="item_profiles")


class LigandResidenceTimeKoffMetricTrace(Base):
    """Metric trace for Autonomous Allosteric Ligand Residence Time & Dissociation Rate Constant (k_off) Molecular Dynamics Extractor."""

    __tablename__ = "p422_ligand_residence_time_koff_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p422_ligand_residence_time_koff_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("LigandResidenceTimeKoffStudy", back_populates="metric_traces")
