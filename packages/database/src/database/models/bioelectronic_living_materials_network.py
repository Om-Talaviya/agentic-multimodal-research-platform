"""SQLAlchemy models for Phase 500: Autonomous Bioelectronic Living Biomaterial Microbial Electron Transport Network Modeler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class BioelectronicLivingMaterialsNetworkStudy(Base):
    """Study record for Autonomous Bioelectronic Living Biomaterial Microbial Electron Transport Network Modeler."""

    __tablename__ = "p500_bioelectronic_living_materials_network_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Geobacter sulfurreducens Engineered Electrically Conductive Cytochrome Pili Hydrogel Matrix")
    analytical_modality = Column(String(100), nullable=False, default="bioelectronic-living-materials")
    matrix_electrical_conductivity_S_per_cm = Column(Float, nullable=False, default=0.85)
    redox_cytochrome_hopping_rate_s_inv = Column(Float, nullable=False, default=420000.0)
    current_density_production_mA_per_cm2 = Column(Float, nullable=False, default=18.5)
    longitudinal_charge_transfer_efficiency = Column(Float, nullable=False, default=0.965)
    confidence_score = Column(Float, nullable=False, default=0.991)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("BioelectronicLivingMaterialsNetworkItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("BioelectronicLivingMaterialsNetworkMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class BioelectronicLivingMaterialsNetworkItemProfile(Base):
    """Detailed item profile for Autonomous Bioelectronic Living Biomaterial Microbial Electron Transport Network Modeler."""

    __tablename__ = "p500_bioelectronic_living_materials_network_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p500_bioelectronic_living_materials_network_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("BioelectronicLivingMaterialsNetworkStudy", back_populates="item_profiles")


class BioelectronicLivingMaterialsNetworkMetricTrace(Base):
    """Metric trace for Autonomous Bioelectronic Living Biomaterial Microbial Electron Transport Network Modeler."""

    __tablename__ = "p500_bioelectronic_living_materials_network_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p500_bioelectronic_living_materials_network_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("BioelectronicLivingMaterialsNetworkStudy", back_populates="metric_traces")
