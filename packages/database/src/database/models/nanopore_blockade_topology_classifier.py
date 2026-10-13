"""SQLAlchemy models for Phase 450: Autonomous Nanopore Ionic Current Blockade Shape Classifier for Macromolecular Topologies."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class NanoporeBlockadeTopologyStudy(Base):
    """Study record for Autonomous Nanopore Ionic Current Blockade Shape Classifier for Macromolecular Topologies."""

    __tablename__ = "p450_nanopore_blockade_topology_classifier_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Supercoiled Plasmid DNA and Knotted Circular Peptides Passing Through 4nm Aerolysin Pore")
    analytical_modality = Column(String(100), nullable=False, default="nanopore-blockade-topology")
    dwell_time_topological_knot_us = Column(Float, nullable=False, default=84.5)
    fractional_blockade_current_depth_ratio = Column(Float, nullable=False, default=0.892)
    topology_classification_accuracy = Column(Float, nullable=False, default=0.978)
    translocation_velocity_nt_per_ms = Column(Float, nullable=False, default=4.2)
    confidence_score = Column(Float, nullable=False, default=0.992)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("NanoporeBlockadeTopologyItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("NanoporeBlockadeTopologyMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class NanoporeBlockadeTopologyItemProfile(Base):
    """Detailed item profile for Autonomous Nanopore Ionic Current Blockade Shape Classifier for Macromolecular Topologies."""

    __tablename__ = "p450_nanopore_blockade_topology_classifier_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p450_nanopore_blockade_topology_classifier_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NanoporeBlockadeTopologyStudy", back_populates="item_profiles")


class NanoporeBlockadeTopologyMetricTrace(Base):
    """Metric trace for Autonomous Nanopore Ionic Current Blockade Shape Classifier for Macromolecular Topologies."""

    __tablename__ = "p450_nanopore_blockade_topology_classifier_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p450_nanopore_blockade_topology_classifier_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NanoporeBlockadeTopologyStudy", back_populates="metric_traces")
