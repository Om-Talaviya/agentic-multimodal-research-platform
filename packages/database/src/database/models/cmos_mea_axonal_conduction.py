"""SQLAlchemy models for Phase 490: Autonomous High-Density CMOS Microelectrode Array Neuromorphic Axonal Conduction Velocity Mapper."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CmosMeaAxonalConductionStudy(Base):
    """Study record for Autonomous High-Density CMOS Microelectrode Array Neuromorphic Axonal Conduction Velocity Mapper."""

    __tablename__ = "p490_cmos_mea_axonal_conduction_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Rat Cortical Primary Neurons Cultured over 26,400 Platinum Electrode CMOS Biocompatible Chip")
    analytical_modality = Column(String(100), nullable=False, default="cmos-mea-axonal-conduction")
    axonal_action_potential_conduction_velocity_m_per_s = Column(Float, nullable=False, default=0.65)
    spike_signal_to_noise_ratio_snr = Column(Float, nullable=False, default=18.2)
    synaptic_propagation_latency_ms = Column(Float, nullable=False, default=1.85)
    functional_synaptic_connectivity_density = Column(Float, nullable=False, default=0.925)
    confidence_score = Column(Float, nullable=False, default=0.993)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CmosMeaAxonalConductionItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("CmosMeaAxonalConductionMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class CmosMeaAxonalConductionItemProfile(Base):
    """Detailed item profile for Autonomous High-Density CMOS Microelectrode Array Neuromorphic Axonal Conduction Velocity Mapper."""

    __tablename__ = "p490_cmos_mea_axonal_conduction_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p490_cmos_mea_axonal_conduction_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CmosMeaAxonalConductionStudy", back_populates="item_profiles")


class CmosMeaAxonalConductionMetricTrace(Base):
    """Metric trace for Autonomous High-Density CMOS Microelectrode Array Neuromorphic Axonal Conduction Velocity Mapper."""

    __tablename__ = "p490_cmos_mea_axonal_conduction_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p490_cmos_mea_axonal_conduction_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CmosMeaAxonalConductionStudy", back_populates="metric_traces")
