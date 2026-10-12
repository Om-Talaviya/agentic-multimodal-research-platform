"""SQLAlchemy models for Phase 426: Autonomous Mass Photometry Macromolecular Oligomeric Mass Distribution & Dissociation Constant (KD) Estimator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MassPhotometryOligomerKdStudy(Base):
    """Study record for Autonomous Mass Photometry Macromolecular Oligomeric Mass Distribution & Dissociation Constant (KD) Estimator."""

    __tablename__ = "p426_mass_photometry_oligomer_kd_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Native Macromolecular Assembly on Glass Coverslip Surface")
    analytical_modality = Column(String(100), nullable=False, default="mass-photometry-kd")
    molecular_mass_kda = Column(Float, nullable=False, default=148.5)
    equilibrium_dissociation_constant_nM = Column(Float, nullable=False, default=18.4)
    dimer_to_monomer_peak_ratio = Column(Float, nullable=False, default=2.85)
    contrast_interferometry_snr = Column(Float, nullable=False, default=42.6)
    confidence_score = Column(Float, nullable=False, default=0.992)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MassPhotometryOligomerKdItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MassPhotometryOligomerKdMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MassPhotometryOligomerKdItemProfile(Base):
    """Detailed item profile for Autonomous Mass Photometry Macromolecular Oligomeric Mass Distribution & Dissociation Constant (KD) Estimator."""

    __tablename__ = "p426_mass_photometry_oligomer_kd_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p426_mass_photometry_oligomer_kd_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MassPhotometryOligomerKdStudy", back_populates="item_profiles")


class MassPhotometryOligomerKdMetricTrace(Base):
    """Metric trace for Autonomous Mass Photometry Macromolecular Oligomeric Mass Distribution & Dissociation Constant (KD) Estimator."""

    __tablename__ = "p426_mass_photometry_oligomer_kd_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p426_mass_photometry_oligomer_kd_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MassPhotometryOligomerKdStudy", back_populates="metric_traces")
