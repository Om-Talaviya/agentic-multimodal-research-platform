"""SQLAlchemy models for Phase 472: Autonomous Synthetic Gene Circuit Cross-Repression Epigenetic Bistable Switch Simulator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class GeneCircuitBistableSwitchStudy(Base):
    """Study record for Autonomous Synthetic Gene Circuit Cross-Repression Epigenetic Bistable Switch Simulator."""

    __tablename__ = "p472_gene_circuit_bistable_switch_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Synthetic LacI-TetR Mutual Inactivation Toggle Switch with Epigenetic DNA Methylation Memory")
    analytical_modality = Column(String(100), nullable=False, default="gene-circuit-bistable-switch")
    bistable_hysteresis_basin_depth_au = Column(Float, nullable=False, default=4.85)
    stochastic_switching_barrier_height_kbT = Column(Float, nullable=False, default=18.2)
    state_transition_retention_half_life_hours = Column(Float, nullable=False, default=144.0)
    cooperative_hill_coefficient = Column(Float, nullable=False, default=2.85)
    confidence_score = Column(Float, nullable=False, default=0.991)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("GeneCircuitBistableSwitchItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("GeneCircuitBistableSwitchMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class GeneCircuitBistableSwitchItemProfile(Base):
    """Detailed item profile for Autonomous Synthetic Gene Circuit Cross-Repression Epigenetic Bistable Switch Simulator."""

    __tablename__ = "p472_gene_circuit_bistable_switch_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p472_gene_circuit_bistable_switch_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("GeneCircuitBistableSwitchStudy", back_populates="item_profiles")


class GeneCircuitBistableSwitchMetricTrace(Base):
    """Metric trace for Autonomous Synthetic Gene Circuit Cross-Repression Epigenetic Bistable Switch Simulator."""

    __tablename__ = "p472_gene_circuit_bistable_switch_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p472_gene_circuit_bistable_switch_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("GeneCircuitBistableSwitchStudy", back_populates="metric_traces")
