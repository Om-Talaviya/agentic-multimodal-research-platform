"""SQLAlchemy models for Phase 574: Autonomous Engineered Probiotic Gastrointestinal In-Vivo Biosurveillance & Colitis Biomarker Logic Gate Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class EngineeredProbioticInVivoBiosurveillanceStudy(Base):
    """Study record for Autonomous Engineered Probiotic Gastrointestinal In-Vivo Biosurveillance & Colitis Biomarker Logic Gate Engine."""

    __tablename__ = "p574_engineered_probiotic_in_vivo_biosurveillance_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Engineered Escherichia coli Nissle 1917 Dual-Input Nitric Oxide and Tetrathionate Responsive Memory Circuit")
    analytical_modality = Column(String(100), nullable=False, default="probiotic-in-vivo-biosurveillance")
    calprotectin_induction_fold_change = Column(Float, nullable=False, default=16.4)
    genetic_circuit_retention_stability = Column(Float, nullable=False, default=0.985)
    gut_colonization_density_cfu_g = Column(Float, nullable=False, default=450000000.0)
    false_positive_activation_rate = Column(Float, nullable=False, default=0.008)
    confidence_score = Column(Float, nullable=False, default=0.996)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("EngineeredProbioticInVivoBiosurveillanceItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("EngineeredProbioticInVivoBiosurveillanceMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class EngineeredProbioticInVivoBiosurveillanceItemProfile(Base):
    """Detailed item profile for Autonomous Engineered Probiotic Gastrointestinal In-Vivo Biosurveillance & Colitis Biomarker Logic Gate Engine."""

    __tablename__ = "p574_engineered_probiotic_in_vivo_biosurveillance_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p574_engineered_probiotic_in_vivo_biosurveillance_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("EngineeredProbioticInVivoBiosurveillanceStudy", back_populates="item_profiles")


class EngineeredProbioticInVivoBiosurveillanceMetricTrace(Base):
    """Metric trace for Autonomous Engineered Probiotic Gastrointestinal In-Vivo Biosurveillance & Colitis Biomarker Logic Gate Engine."""

    __tablename__ = "p574_engineered_probiotic_in_vivo_biosurveillance_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p574_engineered_probiotic_in_vivo_biosurveillance_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("EngineeredProbioticInVivoBiosurveillanceStudy", back_populates="metric_traces")
