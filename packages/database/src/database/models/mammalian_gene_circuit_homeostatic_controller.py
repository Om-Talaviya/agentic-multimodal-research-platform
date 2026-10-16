"""SQLAlchemy models for Phase 556: Autonomous Synthetic Mammalian Gene Circuit Feedback Integral Controller for Homeostatic Glucose Regulation."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MammalianGeneCircuitHomeostaticControllerStudy(Base):
    """Study record for Autonomous Synthetic Mammalian Gene Circuit Feedback Integral Controller for Homeostatic Glucose Regulation."""

    __tablename__ = "p556_mammalian_gene_circuit_homeostatic_controller_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Engineered Beta-Cell Like HEK-293T cells expressing Synthetic Glucose-Sensing Integral Antithetic Feedback Invertible Controller")
    analytical_modality = Column(String(100), nullable=False, default="synthetic-homeostatic-circuit")
    homeostatic_glucose_setpoint_steady_state_mg_dl = Column(Float, nullable=False, default=95.0)
    integral_control_settling_time_minutes = Column(Float, nullable=False, default=42.0)
    steady_state_error_offset_pct = Column(Float, nullable=False, default=0.45)
    insulin_secretion_burst_amplitude_pg_cell = Column(Float, nullable=False, default=18.2)
    confidence_score = Column(Float, nullable=False, default=0.998)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MammalianGeneCircuitHomeostaticControllerItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MammalianGeneCircuitHomeostaticControllerMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MammalianGeneCircuitHomeostaticControllerItemProfile(Base):
    """Detailed item profile for Autonomous Synthetic Mammalian Gene Circuit Feedback Integral Controller for Homeostatic Glucose Regulation."""

    __tablename__ = "p556_mammalian_gene_circuit_homeostatic_controller_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p556_mammalian_gene_circuit_homeostatic_controller_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MammalianGeneCircuitHomeostaticControllerStudy", back_populates="item_profiles")


class MammalianGeneCircuitHomeostaticControllerMetricTrace(Base):
    """Metric trace for Autonomous Synthetic Mammalian Gene Circuit Feedback Integral Controller for Homeostatic Glucose Regulation."""

    __tablename__ = "p556_mammalian_gene_circuit_homeostatic_controller_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p556_mammalian_gene_circuit_homeostatic_controller_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MammalianGeneCircuitHomeostaticControllerStudy", back_populates="metric_traces")
