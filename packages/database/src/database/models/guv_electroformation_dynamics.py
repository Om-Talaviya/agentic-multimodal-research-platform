"""SQLAlchemy models for Phase 480: Autonomous Synthetic Protocellular Giant Unilamellar Vesicle (GUV) Electroformation Simulator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class GuvElectroformationDynamicsStudy(Base):
    """Study record for Autonomous Synthetic Protocellular Giant Unilamellar Vesicle (GUV) Electroformation Simulator."""

    __tablename__ = "p480_guv_electroformation_dynamics_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Indium Tin Oxide (ITO) Microelectrode Chamber with POPC/Cholesterol Bilayer Hydration")
    analytical_modality = Column(String(100), nullable=False, default="guv-electroformation-dynamics")
    guv_mean_diameter_yield_um = Column(Float, nullable=False, default=28.5)
    bilayer_bending_rigidity_kbT = Column(Float, nullable=False, default=22.4)
    electric_field_interfacial_shear_V_per_m = Column(Float, nullable=False, default=1200.0)
    unilamellarity_monodispersity_cv = Column(Float, nullable=False, default=0.065)
    confidence_score = Column(Float, nullable=False, default=0.989)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("GuvElectroformationDynamicsItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("GuvElectroformationDynamicsMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class GuvElectroformationDynamicsItemProfile(Base):
    """Detailed item profile for Autonomous Synthetic Protocellular Giant Unilamellar Vesicle (GUV) Electroformation Simulator."""

    __tablename__ = "p480_guv_electroformation_dynamics_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p480_guv_electroformation_dynamics_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("GuvElectroformationDynamicsStudy", back_populates="item_profiles")


class GuvElectroformationDynamicsMetricTrace(Base):
    """Metric trace for Autonomous Synthetic Protocellular Giant Unilamellar Vesicle (GUV) Electroformation Simulator."""

    __tablename__ = "p480_guv_electroformation_dynamics_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p480_guv_electroformation_dynamics_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("GuvElectroformationDynamicsStudy", back_populates="metric_traces")
