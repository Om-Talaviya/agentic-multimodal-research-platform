"""SQLAlchemy models for Phase 534: Autonomous High-Throughput 3D Microfluidic Dielectrophoresis (DEP) Circulating Tumor Cell Sorter."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MicrofluidicCellSortingDielectrophoresisStudy(Base):
    """Study record for Autonomous High-Throughput 3D Microfluidic Dielectrophoresis (DEP) Circulating Tumor Cell Sorter."""

    __tablename__ = "p534_microfluidic_cell_sorting_dielectrophoresis_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Microfluidic Channel with 3D Quadrupole Electrodes for Label-Free Isolation of Metastatic Breast CTCs")
    analytical_modality = Column(String(100), nullable=False, default="microfluidic-dep-cell-sorting")
    target_cell_recovery_purity_pct = Column(Float, nullable=False, default=96.8)
    sorting_throughput_cells_per_s = Column(Float, nullable=False, default=12500.0)
    dielectrophoretic_crossover_frequency_khz = Column(Float, nullable=False, default=185.0)
    post_sorting_cell_viability_pct = Column(Float, nullable=False, default=98.2)
    confidence_score = Column(Float, nullable=False, default=0.994)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MicrofluidicCellSortingDielectrophoresisItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MicrofluidicCellSortingDielectrophoresisMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MicrofluidicCellSortingDielectrophoresisItemProfile(Base):
    """Detailed item profile for Autonomous High-Throughput 3D Microfluidic Dielectrophoresis (DEP) Circulating Tumor Cell Sorter."""

    __tablename__ = "p534_microfluidic_cell_sorting_dielectrophoresis_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p534_microfluidic_cell_sorting_dielectrophoresis_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MicrofluidicCellSortingDielectrophoresisStudy", back_populates="item_profiles")


class MicrofluidicCellSortingDielectrophoresisMetricTrace(Base):
    """Metric trace for Autonomous High-Throughput 3D Microfluidic Dielectrophoresis (DEP) Circulating Tumor Cell Sorter."""

    __tablename__ = "p534_microfluidic_cell_sorting_dielectrophoresis_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p534_microfluidic_cell_sorting_dielectrophoresis_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MicrofluidicCellSortingDielectrophoresisStudy", back_populates="metric_traces")
