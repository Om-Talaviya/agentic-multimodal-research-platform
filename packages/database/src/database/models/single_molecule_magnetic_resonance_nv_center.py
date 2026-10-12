"""SQLAlchemy models for Phase 436: Autonomous Diamond NV-Center Nanoscale Single-Molecule Magnetic Resonance Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SingleMoleculeNvCenterNmrStudy(Base):
    """Study record for Autonomous Diamond NV-Center Nanoscale Single-Molecule Magnetic Resonance Engine."""

    __tablename__ = "p436_single_molecule_magnetic_resonance_nv_center_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Diamond Nitrogen-Vacancy (NV) Center Nanocrystal with Surface Immobilized Ferritin")
    analytical_modality = Column(String(100), nullable=False, default="nv-center-nanoscale-nmr")
    spin_coherence_time_t2_us = Column(Float, nullable=False, default=145.0)
    magnetic_sensitivity_nT_per_sqrthz = Column(Float, nullable=False, default=2.45)
    optically_detected_mr_dip_contrast = Column(Float, nullable=False, default=0.185)
    spatial_standoff_distance_nm = Column(Float, nullable=False, default=3.2)
    confidence_score = Column(Float, nullable=False, default=0.992)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SingleMoleculeNvCenterNmrItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SingleMoleculeNvCenterNmrMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SingleMoleculeNvCenterNmrItemProfile(Base):
    """Detailed item profile for Autonomous Diamond NV-Center Nanoscale Single-Molecule Magnetic Resonance Engine."""

    __tablename__ = "p436_single_molecule_magnetic_resonance_nv_center_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p436_single_molecule_magnetic_resonance_nv_center_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SingleMoleculeNvCenterNmrStudy", back_populates="item_profiles")


class SingleMoleculeNvCenterNmrMetricTrace(Base):
    """Metric trace for Autonomous Diamond NV-Center Nanoscale Single-Molecule Magnetic Resonance Engine."""

    __tablename__ = "p436_single_molecule_magnetic_resonance_nv_center_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p436_single_molecule_magnetic_resonance_nv_center_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SingleMoleculeNvCenterNmrStudy", back_populates="metric_traces")
