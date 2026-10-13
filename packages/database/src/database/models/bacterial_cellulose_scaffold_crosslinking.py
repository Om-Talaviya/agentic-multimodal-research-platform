"""SQLAlchemy models for Phase 462: Autonomous Living Biomaterial Engineered Bacterial Cellulose Scaffold Cross-Linking Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class BacterialCelluloseScaffoldStudy(Base):
    """Study record for Autonomous Living Biomaterial Engineered Bacterial Cellulose Scaffold Cross-Linking Engine."""

    __tablename__ = "p462_bacterial_cellulose_scaffold_crosslinking_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Komagataeibacter xylinus Pellicle Hydrogel with Genetically Encoded SpyTag/SpyCatcher Nodes")
    analytical_modality = Column(String(100), nullable=False, default="living-bacterial-cellulose")
    youngs_elastic_modulus_megapascals = Column(Float, nullable=False, default=42.5)
    microfibril_crystallinity_index = Column(Float, nullable=False, default=0.865)
    tensile_fracture_toughness_kj_per_m2 = Column(Float, nullable=False, default=18.4)
    water_retention_swelling_ratio = Column(Float, nullable=False, default=14.2)
    confidence_score = Column(Float, nullable=False, default=0.988)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("BacterialCelluloseScaffoldItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("BacterialCelluloseScaffoldMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class BacterialCelluloseScaffoldItemProfile(Base):
    """Detailed item profile for Autonomous Living Biomaterial Engineered Bacterial Cellulose Scaffold Cross-Linking Engine."""

    __tablename__ = "p462_bacterial_cellulose_scaffold_crosslinking_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p462_bacterial_cellulose_scaffold_crosslinking_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("BacterialCelluloseScaffoldStudy", back_populates="item_profiles")


class BacterialCelluloseScaffoldMetricTrace(Base):
    """Metric trace for Autonomous Living Biomaterial Engineered Bacterial Cellulose Scaffold Cross-Linking Engine."""

    __tablename__ = "p462_bacterial_cellulose_scaffold_crosslinking_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p462_bacterial_cellulose_scaffold_crosslinking_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("BacterialCelluloseScaffoldStudy", back_populates="metric_traces")
