"""SQLAlchemy models for Phase 531: Autonomous Spatially-Resolved Optogenetic Mitochondrial Calcium Spark & Bioenergetics Modeler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class OptogeneticMitochondrialCalciumOscillatorStudy(Base):
    """Study record for Autonomous Spatially-Resolved Optogenetic Mitochondrial Calcium Spark & Bioenergetics Modeler."""

    __tablename__ = "p531_optogenetic_mitochondrial_calcium_oscillator_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Cardiomyocyte Syncytium with Mitochondrially-Targeted ChR2 and R-GECO1 Probes")
    analytical_modality = Column(String(100), nullable=False, default="optogenetic-mitochondrial-calcium")
    matrix_calcium_influx_rate_uM_per_s = Column(Float, nullable=False, default=12.4)
    mcu_channel_open_probability = Column(Float, nullable=False, default=0.84)
    atp_production_coupling_gain_pct = Column(Float, nullable=False, default=28.5)
    mptp_opening_prevention_threshold_uM = Column(Float, nullable=False, default=4.2)
    confidence_score = Column(Float, nullable=False, default=0.993)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("OptogeneticMitochondrialCalciumOscillatorItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("OptogeneticMitochondrialCalciumOscillatorMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class OptogeneticMitochondrialCalciumOscillatorItemProfile(Base):
    """Detailed item profile for Autonomous Spatially-Resolved Optogenetic Mitochondrial Calcium Spark & Bioenergetics Modeler."""

    __tablename__ = "p531_optogenetic_mitochondrial_calcium_oscillator_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p531_optogenetic_mitochondrial_calcium_oscillator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OptogeneticMitochondrialCalciumOscillatorStudy", back_populates="item_profiles")


class OptogeneticMitochondrialCalciumOscillatorMetricTrace(Base):
    """Metric trace for Autonomous Spatially-Resolved Optogenetic Mitochondrial Calcium Spark & Bioenergetics Modeler."""

    __tablename__ = "p531_optogenetic_mitochondrial_calcium_oscillator_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p531_optogenetic_mitochondrial_calcium_oscillator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OptogeneticMitochondrialCalciumOscillatorStudy", back_populates="metric_traces")
