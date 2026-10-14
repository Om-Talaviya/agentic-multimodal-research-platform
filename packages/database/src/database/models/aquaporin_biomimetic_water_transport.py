"""SQLAlchemy models for Phase 491: Autonomous Biomimetic Synthetic Membrane Water Aquaporin Channel Transport Forecaster."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class AquaporinBiomimeticWaterTransportStudy(Base):
    """Study record for Autonomous Biomimetic Synthetic Membrane Water Aquaporin Channel Transport Forecaster."""

    __tablename__ = "p491_aquaporin_biomimetic_water_transport_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Polymer-Inorganic Biomimetic Aquaporin-Z Nanocomposite Membrane with Forward Osmosis Crossflow")
    analytical_modality = Column(String(100), nullable=False, default="aquaporin-biomimetic-transport")
    water_permeability_flux_lmh_bar = Column(Float, nullable=False, default=48.5)
    nacl_solute_rejection_percentage = Column(Float, nullable=False, default=99.4)
    aquaporin_channel_incorporation_density_per_um2 = Column(Float, nullable=False, default=12500.0)
    single_pore_osmotic_permeability_pf_cm3_per_s = Column(Float, nullable=False, default=4.2e-14)
    confidence_score = Column(Float, nullable=False, default=0.992)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("AquaporinBiomimeticWaterTransportItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("AquaporinBiomimeticWaterTransportMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class AquaporinBiomimeticWaterTransportItemProfile(Base):
    """Detailed item profile for Autonomous Biomimetic Synthetic Membrane Water Aquaporin Channel Transport Forecaster."""

    __tablename__ = "p491_aquaporin_biomimetic_water_transport_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p491_aquaporin_biomimetic_water_transport_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("AquaporinBiomimeticWaterTransportStudy", back_populates="item_profiles")


class AquaporinBiomimeticWaterTransportMetricTrace(Base):
    """Metric trace for Autonomous Biomimetic Synthetic Membrane Water Aquaporin Channel Transport Forecaster."""

    __tablename__ = "p491_aquaporin_biomimetic_water_transport_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p491_aquaporin_biomimetic_water_transport_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("AquaporinBiomimeticWaterTransportStudy", back_populates="metric_traces")
