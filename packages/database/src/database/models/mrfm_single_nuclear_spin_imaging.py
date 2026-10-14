"""SQLAlchemy models for Phase 499: Autonomous Single-Molecule Magnetic Resonance Force Microscopy 3D Nuclear Spin Imaging Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MrfmSingleNuclearSpinImagingStudy(Base):
    """Study record for Autonomous Single-Molecule Magnetic Resonance Force Microscopy 3D Nuclear Spin Imaging Engine."""

    __tablename__ = "p499_mrfm_single_nuclear_spin_imaging_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Ultra-Sensitive Silicon Nanocantilever with Ferromagnetic SmCo Tip over Vitrified Tobacco Mosaic Virus")
    analytical_modality = Column(String(100), nullable=False, default="mrfm-single-spin-imaging")
    mrfm_spatial_resolution_nm = Column(Float, nullable=False, default=1.85)
    attonewton_force_gradient_sensitivity_aN_per_nm = Column(Float, nullable=False, default=4.2)
    spin_nutation_inversion_fidelity = Column(Float, nullable=False, default=0.985)
    three_d_spin_density_reconstruction_snr = Column(Float, nullable=False, default=19.4)
    confidence_score = Column(Float, nullable=False, default=0.993)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MrfmSingleNuclearSpinImagingItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MrfmSingleNuclearSpinImagingMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MrfmSingleNuclearSpinImagingItemProfile(Base):
    """Detailed item profile for Autonomous Single-Molecule Magnetic Resonance Force Microscopy 3D Nuclear Spin Imaging Engine."""

    __tablename__ = "p499_mrfm_single_nuclear_spin_imaging_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p499_mrfm_single_nuclear_spin_imaging_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MrfmSingleNuclearSpinImagingStudy", back_populates="item_profiles")


class MrfmSingleNuclearSpinImagingMetricTrace(Base):
    """Metric trace for Autonomous Single-Molecule Magnetic Resonance Force Microscopy 3D Nuclear Spin Imaging Engine."""

    __tablename__ = "p499_mrfm_single_nuclear_spin_imaging_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p499_mrfm_single_nuclear_spin_imaging_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MrfmSingleNuclearSpinImagingStudy", back_populates="metric_traces")
