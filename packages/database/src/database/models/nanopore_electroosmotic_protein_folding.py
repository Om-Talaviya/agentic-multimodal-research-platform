"""SQLAlchemy models for Phase 553: Autonomous Nanopore Electro-Osmotic Trap Protein Native State Unfolding & Refolding Kinetics Modeler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class NanoporeElectroosmoticProteinFoldingStudy(Base):
    """Study record for Autonomous Nanopore Electro-Osmotic Trap Protein Native State Unfolding & Refolding Kinetics Modeler."""

    __tablename__ = "p553_nanopore_electroosmotic_protein_folding_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Single Bovine Carbonic Anhydrase II trapped in ClyA Biological Nanopore under Variable Transmembrane Voltage Bias")
    analytical_modality = Column(String(100), nullable=False, default="nanopore-electroosmotic-folding")
    single_molecule_trap_dwell_time_s = Column(Float, nullable=False, default=14.5)
    electroosmotic_holding_force_pn = Column(Float, nullable=False, default=8.2)
    unfolding_activation_free_energy_barrier_kt = Column(Float, nullable=False, default=18.6)
    refolding_transition_rate_per_second = Column(Float, nullable=False, default=32.4)
    confidence_score = Column(Float, nullable=False, default=0.995)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("NanoporeElectroosmoticProteinFoldingItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("NanoporeElectroosmoticProteinFoldingMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class NanoporeElectroosmoticProteinFoldingItemProfile(Base):
    """Detailed item profile for Autonomous Nanopore Electro-Osmotic Trap Protein Native State Unfolding & Refolding Kinetics Modeler."""

    __tablename__ = "p553_nanopore_electroosmotic_protein_folding_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p553_nanopore_electroosmotic_protein_folding_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NanoporeElectroosmoticProteinFoldingStudy", back_populates="item_profiles")


class NanoporeElectroosmoticProteinFoldingMetricTrace(Base):
    """Metric trace for Autonomous Nanopore Electro-Osmotic Trap Protein Native State Unfolding & Refolding Kinetics Modeler."""

    __tablename__ = "p553_nanopore_electroosmotic_protein_folding_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p553_nanopore_electroosmotic_protein_folding_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NanoporeElectroosmoticProteinFoldingStudy", back_populates="metric_traces")
