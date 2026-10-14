"""SQLAlchemy models for Phase 477: Autonomous Nanoscale Cytoskeletal Actin Ring Constriction & Cytokinesis Cleavage Furrow Modeler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class ActinRingCytokinesisConstrictionStudy(Base):
    """Study record for Autonomous Nanoscale Cytoskeletal Actin Ring Constriction & Cytokinesis Cleavage Furrow Modeler."""

    __tablename__ = "p477_actin_ring_cytokinesis_constriction_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Vitrified Dividing S. pombe Protoplast Actomyosin Ring Complex with Myosin-II / Formin Cdc12 Clusters")
    analytical_modality = Column(String(100), nullable=False, default="actin-ring-cytokinesis-constriction")
    contractile_ring_tension_pN = Column(Float, nullable=False, default=480.0)
    furrow_ingression_velocity_nm_per_s = Column(Float, nullable=False, default=2.45)
    actin_filament_turnover_rate_s_inv = Column(Float, nullable=False, default=0.045)
    ring_diameter_constriction_ratio = Column(Float, nullable=False, default=0.885)
    confidence_score = Column(Float, nullable=False, default=0.992)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("ActinRingCytokinesisConstrictionItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("ActinRingCytokinesisConstrictionMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class ActinRingCytokinesisConstrictionItemProfile(Base):
    """Detailed item profile for Autonomous Nanoscale Cytoskeletal Actin Ring Constriction & Cytokinesis Cleavage Furrow Modeler."""

    __tablename__ = "p477_actin_ring_cytokinesis_constriction_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p477_actin_ring_cytokinesis_constriction_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("ActinRingCytokinesisConstrictionStudy", back_populates="item_profiles")


class ActinRingCytokinesisConstrictionMetricTrace(Base):
    """Metric trace for Autonomous Nanoscale Cytoskeletal Actin Ring Constriction & Cytokinesis Cleavage Furrow Modeler."""

    __tablename__ = "p477_actin_ring_cytokinesis_constriction_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p477_actin_ring_cytokinesis_constriction_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("ActinRingCytokinesisConstrictionStudy", back_populates="metric_traces")
