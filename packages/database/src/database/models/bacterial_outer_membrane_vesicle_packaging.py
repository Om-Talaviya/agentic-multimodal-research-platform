"""SQLAlchemy models for Phase 530: Autonomous Bacterial Outer Membrane Vesicle (OMV) Biogenesis & Cargo Sorting Predictor."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class BacterialOuterMembraneVesiclePackagingStudy(Base):
    """Study record for Autonomous Bacterial Outer Membrane Vesicle (OMV) Biogenesis & Cargo Sorting Predictor."""

    __tablename__ = "p530_bacterial_outer_membrane_vesicle_packaging_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Hyper-Vesiculating Engineered Pseudomonas aeruginosa Strain PAO1 Membrane Fractions")
    analytical_modality = Column(String(100), nullable=False, default="omv-biogenesis-cargo-sorting")
    vesiculation_rate_omv_per_cell_hr = Column(Float, nullable=False, default=145.0)
    cargo_virulence_factor_enrichment_ratio = Column(Float, nullable=False, default=8.4)
    vesicle_average_hydrodynamic_diameter_nm = Column(Float, nullable=False, default=82.5)
    lps_phospholipid_asymmetry_index = Column(Float, nullable=False, default=0.94)
    confidence_score = Column(Float, nullable=False, default=0.992)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("BacterialOuterMembraneVesiclePackagingItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("BacterialOuterMembraneVesiclePackagingMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class BacterialOuterMembraneVesiclePackagingItemProfile(Base):
    """Detailed item profile for Autonomous Bacterial Outer Membrane Vesicle (OMV) Biogenesis & Cargo Sorting Predictor."""

    __tablename__ = "p530_bacterial_outer_membrane_vesicle_packaging_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p530_bacterial_outer_membrane_vesicle_packaging_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("BacterialOuterMembraneVesiclePackagingStudy", back_populates="item_profiles")


class BacterialOuterMembraneVesiclePackagingMetricTrace(Base):
    """Metric trace for Autonomous Bacterial Outer Membrane Vesicle (OMV) Biogenesis & Cargo Sorting Predictor."""

    __tablename__ = "p530_bacterial_outer_membrane_vesicle_packaging_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p530_bacterial_outer_membrane_vesicle_packaging_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("BacterialOuterMembraneVesiclePackagingStudy", back_populates="metric_traces")
