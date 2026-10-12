"""SQLAlchemy models for Phase 419: Autonomous In-Cell NMR Macromolecular Crowding & Chemical Shift Perturbation Tensor Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class InCellNmrCrowdingTensorStudy(Base):
    """Study record for Autonomous In-Cell NMR Macromolecular Crowding & Chemical Shift Perturbation Tensor Engine."""

    __tablename__ = "p419_in_cell_nmr_crowding_tensor_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="15N/13C-Enriched Intact E. coli Cytoplasm with Model Protein")
    analytical_modality = Column(String(100), nullable=False, default="in-cell-nmr")
    chemical_shift_perturbation_ppm = Column(Float, nullable=False, default=0.142)
    rotational_correlation_time_ns = Column(Float, nullable=False, default=18.4)
    crowding_viscosity_factor = Column(Float, nullable=False, default=2.85)
    transverse_relaxation_r2_rate = Column(Float, nullable=False, default=32.1)
    confidence_score = Column(Float, nullable=False, default=0.982)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("InCellNmrCrowdingTensorItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("InCellNmrCrowdingTensorMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class InCellNmrCrowdingTensorItemProfile(Base):
    """Detailed item profile for Autonomous In-Cell NMR Macromolecular Crowding & Chemical Shift Perturbation Tensor Engine."""

    __tablename__ = "p419_in_cell_nmr_crowding_tensor_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p419_in_cell_nmr_crowding_tensor_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("InCellNmrCrowdingTensorStudy", back_populates="item_profiles")


class InCellNmrCrowdingTensorMetricTrace(Base):
    """Metric trace for Autonomous In-Cell NMR Macromolecular Crowding & Chemical Shift Perturbation Tensor Engine."""

    __tablename__ = "p419_in_cell_nmr_crowding_tensor_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p419_in_cell_nmr_crowding_tensor_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("InCellNmrCrowdingTensorStudy", back_populates="metric_traces")
