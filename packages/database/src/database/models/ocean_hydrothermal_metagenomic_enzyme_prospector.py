"""SQLAlchemy models for Phase 561: Autonomous High-Throughput Deep Ocean Hydrothermal Vent Metagenomic Novel Enzyme Prospector."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class OceanHydrothermalMetagenomicEnzymeProspectorStudy(Base):
    """Study record for Autonomous High-Throughput Deep Ocean Hydrothermal Vent Metagenomic Novel Enzyme Prospector."""

    __tablename__ = "p561_ocean_hydrothermal_metagenomic_enzyme_prospector_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Deep-Sea Metagenomic DNA from Mid-Atlantic Ridge Black Smoker Vent Hydrothermal Fluid at 320C and 300 Bar")
    analytical_modality = Column(String(100), nullable=False, default="deep-sea-metagenomic-biocatalysis")
    thermostable_extremozyme_catalytic_half_life_hours = Column(Float, nullable=False, default=72.0)
    novel_biocatalytic_family_discovery_count = Column(Float, nullable=False, default=34.0)
    piezophilic_activation_volume_delta_v_ml_mol = Column(Float, nullable=False, default=-28.5)
    optimum_catalytic_temperature_celsius = Column(Float, nullable=False, default=108.5)
    confidence_score = Column(Float, nullable=False, default=0.995)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("OceanHydrothermalMetagenomicEnzymeProspectorItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("OceanHydrothermalMetagenomicEnzymeProspectorMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class OceanHydrothermalMetagenomicEnzymeProspectorItemProfile(Base):
    """Detailed item profile for Autonomous High-Throughput Deep Ocean Hydrothermal Vent Metagenomic Novel Enzyme Prospector."""

    __tablename__ = "p561_ocean_hydrothermal_metagenomic_enzyme_prospector_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p561_ocean_hydrothermal_metagenomic_enzyme_prospector_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OceanHydrothermalMetagenomicEnzymeProspectorStudy", back_populates="item_profiles")


class OceanHydrothermalMetagenomicEnzymeProspectorMetricTrace(Base):
    """Metric trace for Autonomous High-Throughput Deep Ocean Hydrothermal Vent Metagenomic Novel Enzyme Prospector."""

    __tablename__ = "p561_ocean_hydrothermal_metagenomic_enzyme_prospector_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p561_ocean_hydrothermal_metagenomic_enzyme_prospector_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OceanHydrothermalMetagenomicEnzymeProspectorStudy", back_populates="metric_traces")
