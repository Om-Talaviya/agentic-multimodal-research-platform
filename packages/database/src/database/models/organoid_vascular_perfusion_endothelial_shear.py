"""SQLAlchemy models for Phase 510: Autonomous Vascularized Cerebral Organoid Lumen Shear Stress & Perfusion Simulator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class OrganoidVascularPerfusionEndothelialShearStudy(Base):
    """Study record for Autonomous Vascularized Cerebral Organoid Lumen Shear Stress & Perfusion Simulator."""

    __tablename__ = "p510_organoid_vascular_perfusion_endothelial_shear_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="3D Bioprinted Endothelialized Hydrogel Microchannel Lattice Interfaced with Cortical Brain Organoids")
    analytical_modality = Column(String(100), nullable=False, default="organoid-microvascular-perfusion")
    microvascular_lumen_wall_shear_stress_pa = Column(Float, nullable=False, default=1.45)
    interstitial_oxygen_partial_pressure_mmHg = Column(Float, nullable=False, default=38.5)
    core_necrotic_zone_reduction_ratio = Column(Float, nullable=False, default=0.945)
    tight_junction_claudin5_teer_ohm_cm2 = Column(Float, nullable=False, default=1850.0)
    confidence_score = Column(Float, nullable=False, default=0.995)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("OrganoidVascularPerfusionEndothelialShearItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("OrganoidVascularPerfusionEndothelialShearMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class OrganoidVascularPerfusionEndothelialShearItemProfile(Base):
    """Detailed item profile for Autonomous Vascularized Cerebral Organoid Lumen Shear Stress & Perfusion Simulator."""

    __tablename__ = "p510_organoid_vascular_perfusion_endothelial_shear_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p510_organoid_vascular_perfusion_endothelial_shear_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OrganoidVascularPerfusionEndothelialShearStudy", back_populates="item_profiles")


class OrganoidVascularPerfusionEndothelialShearMetricTrace(Base):
    """Metric trace for Autonomous Vascularized Cerebral Organoid Lumen Shear Stress & Perfusion Simulator."""

    __tablename__ = "p510_organoid_vascular_perfusion_endothelial_shear_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p510_organoid_vascular_perfusion_endothelial_shear_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OrganoidVascularPerfusionEndothelialShearStudy", back_populates="metric_traces")
