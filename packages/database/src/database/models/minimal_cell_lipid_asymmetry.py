"""SQLAlchemy models for Phase 423: Autonomous Synthetic Minimal Cell Membrane Lipid Bilayer Asymmetry & Vesicle Budding Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MinimalCellLipidAsymmetryStudy(Base):
    """Study record for Autonomous Synthetic Minimal Cell Membrane Lipid Bilayer Asymmetry & Vesicle Budding Engine."""

    __tablename__ = "p423_minimal_cell_lipid_asymmetry_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Synthetic Giant Unilamellar Vesicle (GUV) with Flippase ABCB4")
    analytical_modality = Column(String(100), nullable=False, default="minimal-cell-lipid")
    bilayer_asymmetry_index = Column(Float, nullable=False, default=0.884)
    membrane_bending_rigidity_kbt = Column(Float, nullable=False, default=18.2)
    vesicle_budding_rate_um_per_min = Column(Float, nullable=False, default=0.35)
    inner_leaflet_phosphatidylserine_ratio = Column(Float, nullable=False, default=0.912)
    confidence_score = Column(Float, nullable=False, default=0.986)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MinimalCellLipidAsymmetryItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MinimalCellLipidAsymmetryMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MinimalCellLipidAsymmetryItemProfile(Base):
    """Detailed item profile for Autonomous Synthetic Minimal Cell Membrane Lipid Bilayer Asymmetry & Vesicle Budding Engine."""

    __tablename__ = "p423_minimal_cell_lipid_asymmetry_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p423_minimal_cell_lipid_asymmetry_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MinimalCellLipidAsymmetryStudy", back_populates="item_profiles")


class MinimalCellLipidAsymmetryMetricTrace(Base):
    """Metric trace for Autonomous Synthetic Minimal Cell Membrane Lipid Bilayer Asymmetry & Vesicle Budding Engine."""

    __tablename__ = "p423_minimal_cell_lipid_asymmetry_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p423_minimal_cell_lipid_asymmetry_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MinimalCellLipidAsymmetryStudy", back_populates="metric_traces")
