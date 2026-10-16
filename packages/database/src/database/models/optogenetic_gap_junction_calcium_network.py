"""SQLAlchemy models for Phase 554: Autonomous Optogenetic Intercellular Gap Junction Coupling & Calcium Synchrony Network Forecaster."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class OptogeneticGapJunctionCalciumNetworkStudy(Base):
    """Study record for Autonomous Optogenetic Intercellular Gap Junction Coupling & Calcium Synchrony Network Forecaster."""

    __tablename__ = "p554_optogenetic_gap_junction_calcium_network_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Confluent Monolayer of Human Induced Pluripotent Stem Cell-Derived Cardiomyocytes expressing Channelrhodopsin-2 and Connexin-43")
    analytical_modality = Column(String(100), nullable=False, default="optogenetic-gap-junction-sync")
    calcium_wave_propagation_velocity_um_s = Column(Float, nullable=False, default=380.0)
    connexin43_gap_junction_conductance_ns = Column(Float, nullable=False, default=42.5)
    network_phase_synchronization_order_param = Column(Float, nullable=False, default=0.965)
    action_potential_duration_apd90_ms = Column(Float, nullable=False, default=310.0)
    confidence_score = Column(Float, nullable=False, default=0.996)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("OptogeneticGapJunctionCalciumNetworkItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("OptogeneticGapJunctionCalciumNetworkMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class OptogeneticGapJunctionCalciumNetworkItemProfile(Base):
    """Detailed item profile for Autonomous Optogenetic Intercellular Gap Junction Coupling & Calcium Synchrony Network Forecaster."""

    __tablename__ = "p554_optogenetic_gap_junction_calcium_network_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p554_optogenetic_gap_junction_calcium_network_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OptogeneticGapJunctionCalciumNetworkStudy", back_populates="item_profiles")


class OptogeneticGapJunctionCalciumNetworkMetricTrace(Base):
    """Metric trace for Autonomous Optogenetic Intercellular Gap Junction Coupling & Calcium Synchrony Network Forecaster."""

    __tablename__ = "p554_optogenetic_gap_junction_calcium_network_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p554_optogenetic_gap_junction_calcium_network_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OptogeneticGapJunctionCalciumNetworkStudy", back_populates="metric_traces")
