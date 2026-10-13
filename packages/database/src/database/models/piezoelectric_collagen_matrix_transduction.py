"""SQLAlchemy models for Phase 470: Autonomous Bio-Piezoelectric Collagen Matrix Electromechanical Transduction Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class PiezoelectricCollagenMatrixTransductionStudy(Base):
    """Study record for Autonomous Bio-Piezoelectric Collagen Matrix Electromechanical Transduction Engine."""

    __tablename__ = "p470_piezoelectric_collagen_matrix_transduction_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Dense Fibrillar Type-I Collagen Fascicle Scaffold with Applied High-Frequency Axial Dynamic Strain")
    analytical_modality = Column(String(100), nullable=False, default="piezoelectric-collagen-transduction")
    piezoelectric_coefficient_d33_pC_per_N = Column(Float, nullable=False, default=8.45)
    surface_potential_streaming_voltage_mV = Column(Float, nullable=False, default=42.0)
    dynamic_electromechanical_coupling_factor = Column(Float, nullable=False, default=0.285)
    osteogenic_mineralization_acceleration_index = Column(Float, nullable=False, default=2.65)
    confidence_score = Column(Float, nullable=False, default=0.988)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("PiezoelectricCollagenMatrixTransductionItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("PiezoelectricCollagenMatrixTransductionMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class PiezoelectricCollagenMatrixTransductionItemProfile(Base):
    """Detailed item profile for Autonomous Bio-Piezoelectric Collagen Matrix Electromechanical Transduction Engine."""

    __tablename__ = "p470_piezoelectric_collagen_matrix_transduction_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p470_piezoelectric_collagen_matrix_transduction_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("PiezoelectricCollagenMatrixTransductionStudy", back_populates="item_profiles")


class PiezoelectricCollagenMatrixTransductionMetricTrace(Base):
    """Metric trace for Autonomous Bio-Piezoelectric Collagen Matrix Electromechanical Transduction Engine."""

    __tablename__ = "p470_piezoelectric_collagen_matrix_transduction_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p470_piezoelectric_collagen_matrix_transduction_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("PiezoelectricCollagenMatrixTransductionStudy", back_populates="metric_traces")
