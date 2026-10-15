"""SQLAlchemy models for Phase 541: Autonomous Synthetic Protocellular Compartment FtsZ-Min System Dynamic Cleavage Constriction Modeler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SyntheticCellDivisionFtszConstrictionStudy(Base):
    """Study record for Autonomous Synthetic Protocellular Compartment FtsZ-Min System Dynamic Cleavage Constriction Modeler."""

    __tablename__ = "p541_synthetic_cell_division_ftsz_constriction_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Cell-Free Microfluidic Giant Unilamellar Vesicle with Reconstituted FtsZ-FtsA and MinCDE Oscillatory Machinery")
    analytical_modality = Column(String(100), nullable=False, default="protocell-ftsz-cleavage-constriction")
    equatorial_constriction_pinching_force_pN = Column(Float, nullable=False, default=34.0)
    min_protein_pole_to_pole_oscillation_period_s = Column(Float, nullable=False, default=48.0)
    symmetric_daughter_vesicle_yield_pct = Column(Float, nullable=False, default=88.5)
    ftsz_treadmilling_velocity_nm_per_s = Column(Float, nullable=False, default=28.0)
    confidence_score = Column(Float, nullable=False, default=0.994)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("SyntheticCellDivisionFtszConstrictionItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("SyntheticCellDivisionFtszConstrictionMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class SyntheticCellDivisionFtszConstrictionItemProfile(Base):
    """Detailed item profile for Autonomous Synthetic Protocellular Compartment FtsZ-Min System Dynamic Cleavage Constriction Modeler."""

    __tablename__ = "p541_synthetic_cell_division_ftsz_constriction_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p541_synthetic_cell_division_ftsz_constriction_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SyntheticCellDivisionFtszConstrictionStudy", back_populates="item_profiles")


class SyntheticCellDivisionFtszConstrictionMetricTrace(Base):
    """Metric trace for Autonomous Synthetic Protocellular Compartment FtsZ-Min System Dynamic Cleavage Constriction Modeler."""

    __tablename__ = "p541_synthetic_cell_division_ftsz_constriction_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p541_synthetic_cell_division_ftsz_constriction_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("SyntheticCellDivisionFtszConstrictionStudy", back_populates="metric_traces")
