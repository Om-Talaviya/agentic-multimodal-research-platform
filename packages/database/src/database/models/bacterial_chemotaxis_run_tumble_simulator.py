"""SQLAlchemy models for Phase 439: Autonomous Flagellar Motor Stochastic Switching & Bacterial Chemotaxis Run-Tumble Trajectory Simulator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class BacterialChemotaxisSimulatorStudy(Base):
    """Study record for Autonomous Flagellar Motor Stochastic Switching & Bacterial Chemotaxis Run-Tumble Trajectory Simulator."""

    __tablename__ = "p439_bacterial_chemotaxis_run_tumble_simulator_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="E. coli K-12 Motile Swarm in Microfluidic Attractant/Repellent Gradient")
    analytical_modality = Column(String(100), nullable=False, default="chemotaxis-run-tumble")
    run_duration_mean_seconds = Column(Float, nullable=False, default=1.25)
    tumble_frequency_hz = Column(Float, nullable=False, default=0.45)
    chemotactic_drift_velocity_um_per_s = Column(Float, nullable=False, default=8.42)
    chey_p_phosphorylation_equilibrium = Column(Float, nullable=False, default=0.32)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("BacterialChemotaxisSimulatorItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("BacterialChemotaxisSimulatorMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class BacterialChemotaxisSimulatorItemProfile(Base):
    """Detailed item profile for Autonomous Flagellar Motor Stochastic Switching & Bacterial Chemotaxis Run-Tumble Trajectory Simulator."""

    __tablename__ = "p439_bacterial_chemotaxis_run_tumble_simulator_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p439_bacterial_chemotaxis_run_tumble_simulator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("BacterialChemotaxisSimulatorStudy", back_populates="item_profiles")


class BacterialChemotaxisSimulatorMetricTrace(Base):
    """Metric trace for Autonomous Flagellar Motor Stochastic Switching & Bacterial Chemotaxis Run-Tumble Trajectory Simulator."""

    __tablename__ = "p439_bacterial_chemotaxis_run_tumble_simulator_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p439_bacterial_chemotaxis_run_tumble_simulator_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("BacterialChemotaxisSimulatorStudy", back_populates="metric_traces")
