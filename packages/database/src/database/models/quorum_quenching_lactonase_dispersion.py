"""SQLAlchemy models for Phase 485: Autonomous Bacterial Quorum Quenching Enzymatic Lactonase Biofilm Dispersion Forecaster."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class QuorumQuenchingLactonaseDispersionStudy(Base):
    """Study record for Autonomous Bacterial Quorum Quenching Enzymatic Lactonase Biofilm Dispersion Forecaster."""

    __tablename__ = "p485_quorum_quenching_lactonase_dispersion_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Pseudomonas aeruginosa PAO1 Mature Biofilm with Immobilized Phosphotriesterase-Like Lactonase (PLL)")
    analytical_modality = Column(String(100), nullable=False, default="quorum-quenching-lactonase")
    ahl_hydrolysis_kcat_over_km_M_inv_s_inv = Column(Float, nullable=False, default=280000.0)
    biofilm_extracellular_matrix_reduction_pct = Column(Float, nullable=False, default=78.5)
    quorum_regulated_pyocyanin_suppression_pct = Column(Float, nullable=False, default=92.4)
    antibiotic_potency_synergy_fold_increase = Column(Float, nullable=False, default=6.4)
    confidence_score = Column(Float, nullable=False, default=0.988)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("QuorumQuenchingLactonaseDispersionItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("QuorumQuenchingLactonaseDispersionMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class QuorumQuenchingLactonaseDispersionItemProfile(Base):
    """Detailed item profile for Autonomous Bacterial Quorum Quenching Enzymatic Lactonase Biofilm Dispersion Forecaster."""

    __tablename__ = "p485_quorum_quenching_lactonase_dispersion_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p485_quorum_quenching_lactonase_dispersion_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("QuorumQuenchingLactonaseDispersionStudy", back_populates="item_profiles")


class QuorumQuenchingLactonaseDispersionMetricTrace(Base):
    """Metric trace for Autonomous Bacterial Quorum Quenching Enzymatic Lactonase Biofilm Dispersion Forecaster."""

    __tablename__ = "p485_quorum_quenching_lactonase_dispersion_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p485_quorum_quenching_lactonase_dispersion_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("QuorumQuenchingLactonaseDispersionStudy", back_populates="metric_traces")
