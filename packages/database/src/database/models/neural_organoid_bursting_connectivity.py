"""SQLAlchemy models for Phase 463: Autonomous Neural Organoid Spontaneous Synchronous Bursting & Functional Connectivity Grapher."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class NeuralOrganoidBurstingConnectivityStudy(Base):
    """Study record for Autonomous Neural Organoid Spontaneous Synchronous Bursting & Functional Connectivity Grapher."""

    __tablename__ = "p463_neural_organoid_bursting_connectivity_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="6-Month Human Cerebral Cortical Organoid on 4096-Channel CMOS High-Density MEA")
    analytical_modality = Column(String(100), nullable=False, default="organoid-neural-connectivity")
    synchronous_network_burst_rate_hz = Column(Float, nullable=False, default=0.35)
    graph_small_world_clustering_coefficient = Column(Float, nullable=False, default=0.785)
    cross_correlation_functional_connectivity_density = Column(Float, nullable=False, default=0.842)
    shannon_entropy_burst_complexity = Column(Float, nullable=False, default=3.42)
    confidence_score = Column(Float, nullable=False, default=0.992)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("NeuralOrganoidBurstingConnectivityItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("NeuralOrganoidBurstingConnectivityMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class NeuralOrganoidBurstingConnectivityItemProfile(Base):
    """Detailed item profile for Autonomous Neural Organoid Spontaneous Synchronous Bursting & Functional Connectivity Grapher."""

    __tablename__ = "p463_neural_organoid_bursting_connectivity_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p463_neural_organoid_bursting_connectivity_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NeuralOrganoidBurstingConnectivityStudy", back_populates="item_profiles")


class NeuralOrganoidBurstingConnectivityMetricTrace(Base):
    """Metric trace for Autonomous Neural Organoid Spontaneous Synchronous Bursting & Functional Connectivity Grapher."""

    __tablename__ = "p463_neural_organoid_bursting_connectivity_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p463_neural_organoid_bursting_connectivity_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NeuralOrganoidBurstingConnectivityStudy", back_populates="metric_traces")
