"""SQLAlchemy models for Phase 508: Autonomous Solid-State Nanopore Single-Molecule Protein Co-Translocational Unfolding Modeler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SolidStateNanoporeProteinUnfoldingStudy(Base):
    """Study record for Autonomous Solid-State Nanopore Single-Molecule Protein Co-Translocational Unfolding Modeler."""

    __tablename__ = "p508_solid_state_nanopore_protein_unfolding_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Sub-3nm Low-Noise HfO2 Nanopore with ClpX-Coupled Maltose-Binding Protein Translocation")
    analytical_modality = Column(String(100), nullable=False, default="nanopore-protein-unfolding")
    unfolding_energy_barrier_height_kbT = Column(Float, nullable=False, default=24.5)
    translocation_dwell_time_per_domain_ms = Column(Float, nullable=False, default=8.2)
    residual_current_fraction_blockade = Column(Float, nullable=False, default=0.765)
    single_amino_acid_substitutional_snr = Column(Float, nullable=False, default=16.5)
    confidence_score = Column(Float, nullable=False, default=0.993)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SolidStateNanoporeProteinUnfoldingItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SolidStateNanoporeProteinUnfoldingMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SolidStateNanoporeProteinUnfoldingItemProfile(Base):
    """Detailed item profile for Autonomous Solid-State Nanopore Single-Molecule Protein Co-Translocational Unfolding Modeler."""

    __tablename__ = "p508_solid_state_nanopore_protein_unfolding_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p508_solid_state_nanopore_protein_unfolding_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SolidStateNanoporeProteinUnfoldingStudy", back_populates="item_profiles")


class SolidStateNanoporeProteinUnfoldingMetricTrace(Base):
    """Metric trace for Autonomous Solid-State Nanopore Single-Molecule Protein Co-Translocational Unfolding Modeler."""

    __tablename__ = "p508_solid_state_nanopore_protein_unfolding_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p508_solid_state_nanopore_protein_unfolding_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SolidStateNanoporeProteinUnfoldingStudy", back_populates="metric_traces")
