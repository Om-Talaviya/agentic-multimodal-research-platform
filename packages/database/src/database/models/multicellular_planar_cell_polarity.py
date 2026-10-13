"""SQLAlchemy models for Phase 459: Autonomous Synthetic Multicellular Planar Cell Polarity (PCP) Asymmetric Segregation Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MulticellularPlanarCellPolarityStudy(Base):
    """Study record for Autonomous Synthetic Multicellular Planar Cell Polarity (PCP) Asymmetric Segregation Engine."""

    __tablename__ = "p459_multicellular_planar_cell_polarity_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Engineered Epithelial Monolayer with Frizzled-6/Vangl2 Core Protein Polarized Ensembles")
    analytical_modality = Column(String(100), nullable=False, default="planar-cell-polarity-segregation")
    asymmetric_crescent_enrichment_ratio = Column(Float, nullable=False, default=4.25)
    nematic_order_director_coherence = Column(Float, nullable=False, default=0.885)
    junctional_remodeling_strain_rate_per_hr = Column(Float, nullable=False, default=0.042)
    global_polarization_vector_magnitude = Column(Float, nullable=False, default=0.942)
    confidence_score = Column(Float, nullable=False, default=0.989)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MulticellularPlanarCellPolarityItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MulticellularPlanarCellPolarityMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MulticellularPlanarCellPolarityItemProfile(Base):
    """Detailed item profile for Autonomous Synthetic Multicellular Planar Cell Polarity (PCP) Asymmetric Segregation Engine."""

    __tablename__ = "p459_multicellular_planar_cell_polarity_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p459_multicellular_planar_cell_polarity_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MulticellularPlanarCellPolarityStudy", back_populates="item_profiles")


class MulticellularPlanarCellPolarityMetricTrace(Base):
    """Metric trace for Autonomous Synthetic Multicellular Planar Cell Polarity (PCP) Asymmetric Segregation Engine."""

    __tablename__ = "p459_multicellular_planar_cell_polarity_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p459_multicellular_planar_cell_polarity_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MulticellularPlanarCellPolarityStudy", back_populates="metric_traces")
