"""SQLAlchemy models for Phase 568: Autonomous Engineered Bacterial Chemotactic Micro-Biohybrid Swimmer Targeted Navigation & Tumble-Run Kinetics Simulator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class BacterialChemotacticMicroBiohybridSwimmerStudy(Base):
    """Study record for Autonomous Engineered Bacterial Chemotactic Micro-Biohybrid Swimmer Targeted Navigation & Tumble-Run Kinetics Simulator."""

    __tablename__ = "p568_bacterial_chemotactic_micro_biohybrid_swimmer_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Engineered Escherichia coli MG1655 Flagellar Micro-Biohybrid Swimmers in Attractant Aspartate Microfluidic Gradient")
    analytical_modality = Column(String(100), nullable=False, default="bacterial-chemotactic-biohybrid-simulation")
    chemotactic_drift_velocity_um_s = Column(Float, nullable=False, default=18.5)
    run_tumble_frequency_ratio = Column(Float, nullable=False, default=4.2)
    target_accumulation_index = Column(Float, nullable=False, default=0.92)
    flagellar_motor_torque_efficiency = Column(Float, nullable=False, default=0.88)
    confidence_score = Column(Float, nullable=False, default=0.995)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("BacterialChemotacticMicroBiohybridSwimmerItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("BacterialChemotacticMicroBiohybridSwimmerMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class BacterialChemotacticMicroBiohybridSwimmerItemProfile(Base):
    """Detailed item profile for Autonomous Engineered Bacterial Chemotactic Micro-Biohybrid Swimmer Targeted Navigation & Tumble-Run Kinetics Simulator."""

    __tablename__ = "p568_bacterial_chemotactic_micro_biohybrid_swimmer_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p568_bacterial_chemotactic_micro_biohybrid_swimmer_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("BacterialChemotacticMicroBiohybridSwimmerStudy", back_populates="item_profiles")


class BacterialChemotacticMicroBiohybridSwimmerMetricTrace(Base):
    """Metric trace for Autonomous Engineered Bacterial Chemotactic Micro-Biohybrid Swimmer Targeted Navigation & Tumble-Run Kinetics Simulator."""

    __tablename__ = "p568_bacterial_chemotactic_micro_biohybrid_swimmer_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p568_bacterial_chemotactic_micro_biohybrid_swimmer_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("BacterialChemotacticMicroBiohybridSwimmerStudy", back_populates="metric_traces")
