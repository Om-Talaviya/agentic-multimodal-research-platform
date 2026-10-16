"""SQLAlchemy models for Phase 570: Autonomous Synthetic DNA Strand Displacement (DSD) Molecular Neural Network Winner-Take-All Classifier Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SyntheticDnaStrandDisplacementNeuralGateStudy(Base):
    """Study record for Autonomous Synthetic DNA Strand Displacement (DSD) Molecular Neural Network Winner-Take-All Classifier Engine."""

    __tablename__ = "p570_synthetic_dna_strand_displacement_neural_gate_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Toehold-Mediated 4-Input 2-Class DNA Strand Displacement Reaction Network in Tris-Acetate-EDTA Buffer")
    analytical_modality = Column(String(100), nullable=False, default="dsd-molecular-neural-classification")
    toehold_exchange_rate_constant_m_s = Column(Float, nullable=False, default=350000.0)
    signal_to_leakage_ratio = Column(Float, nullable=False, default=28.5)
    winner_take_all_convergence_time_s = Column(Float, nullable=False, default=185.0)
    decision_boundary_sharpness = Column(Float, nullable=False, default=0.965)
    confidence_score = Column(Float, nullable=False, default=0.997)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SyntheticDnaStrandDisplacementNeuralGateItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SyntheticDnaStrandDisplacementNeuralGateMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SyntheticDnaStrandDisplacementNeuralGateItemProfile(Base):
    """Detailed item profile for Autonomous Synthetic DNA Strand Displacement (DSD) Molecular Neural Network Winner-Take-All Classifier Engine."""

    __tablename__ = "p570_synthetic_dna_strand_displacement_neural_gate_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p570_synthetic_dna_strand_displacement_neural_gate_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SyntheticDnaStrandDisplacementNeuralGateStudy", back_populates="item_profiles")


class SyntheticDnaStrandDisplacementNeuralGateMetricTrace(Base):
    """Metric trace for Autonomous Synthetic DNA Strand Displacement (DSD) Molecular Neural Network Winner-Take-All Classifier Engine."""

    __tablename__ = "p570_synthetic_dna_strand_displacement_neural_gate_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p570_synthetic_dna_strand_displacement_neural_gate_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SyntheticDnaStrandDisplacementNeuralGateStudy", back_populates="metric_traces")
