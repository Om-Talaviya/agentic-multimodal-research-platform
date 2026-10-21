"""SQLAlchemy models for Phase 577: Autonomous Microfluidic Droplet-Based Directed Evolution & Enzyme Fitness Landscape Navigator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MicrofluidicDropletDirectedEvolutionStudy(Base):
    """Study record for Autonomous Microfluidic Droplet-Based Directed Evolution & Enzyme Fitness Landscape Navigator."""

    __tablename__ = "p577_microfluidic_droplet_directed_evolution_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Picoliter Water-in-Oil Droplet Encapsulated TEM-1 β-Lactamase Saturation Mutagenesis Library")
    analytical_modality = Column(String(100), nullable=False, default="microfluidic-droplet-directed-evolution")
    droplet_generation_rate_hz = Column(Float, nullable=False, default=12500.0)
    enzyme_kcat_fold_improvement = Column(Float, nullable=False, default=8.4)
    fitness_landscape_ruggedness_index = Column(Float, nullable=False, default=0.62)
    epistatic_interaction_coefficient = Column(Float, nullable=False, default=0.38)
    confidence_score = Column(Float, nullable=False, default=0.996)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MicrofluidicDropletDirectedEvolutionItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MicrofluidicDropletDirectedEvolutionMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MicrofluidicDropletDirectedEvolutionItemProfile(Base):
    """Detailed item profile for Autonomous Microfluidic Droplet-Based Directed Evolution & Enzyme Fitness Landscape Navigator."""

    __tablename__ = "p577_microfluidic_droplet_directed_evolution_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p577_microfluidic_droplet_directed_evolution_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MicrofluidicDropletDirectedEvolutionStudy", back_populates="item_profiles")


class MicrofluidicDropletDirectedEvolutionMetricTrace(Base):
    """Metric trace for Autonomous Microfluidic Droplet-Based Directed Evolution & Enzyme Fitness Landscape Navigator."""

    __tablename__ = "p577_microfluidic_droplet_directed_evolution_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p577_microfluidic_droplet_directed_evolution_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MicrofluidicDropletDirectedEvolutionStudy", back_populates="metric_traces")
