"""SQLAlchemy models for Phase 468: Autonomous Synthetic Morphogenetic Morpho-Kinetic Boundary Sharpening & Eph-Ephrin Repulsion Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class EphEphrinMorphoRepulsionStudy(Base):
    """Study record for Autonomous Synthetic Morphogenetic Morpho-Kinetic Boundary Sharpening & Eph-Ephrin Repulsion Engine."""

    __tablename__ = "p468_eph_ephrin_morpho_repulsion_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="HEK293T EphB2/EphrinB1 Co-Culture Mosaic Boundary Array in Micropatterned Substrates")
    analytical_modality = Column(String(100), nullable=False, default="eph-ephrin-morpho-repulsion")
    interface_roughness_boundary_width_um = Column(Float, nullable=False, default=6.8)
    eph_receptor_clustering_density_per_um2 = Column(Float, nullable=False, default=420.0)
    contact_repulsion_retraction_velocity_um_min = Column(Float, nullable=False, default=2.45)
    heterotypic_sorting_order_parameter = Column(Float, nullable=False, default=0.945)
    confidence_score = Column(Float, nullable=False, default=0.99)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("EphEphrinMorphoRepulsionItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("EphEphrinMorphoRepulsionMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class EphEphrinMorphoRepulsionItemProfile(Base):
    """Detailed item profile for Autonomous Synthetic Morphogenetic Morpho-Kinetic Boundary Sharpening & Eph-Ephrin Repulsion Engine."""

    __tablename__ = "p468_eph_ephrin_morpho_repulsion_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p468_eph_ephrin_morpho_repulsion_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("EphEphrinMorphoRepulsionStudy", back_populates="item_profiles")


class EphEphrinMorphoRepulsionMetricTrace(Base):
    """Metric trace for Autonomous Synthetic Morphogenetic Morpho-Kinetic Boundary Sharpening & Eph-Ephrin Repulsion Engine."""

    __tablename__ = "p468_eph_ephrin_morpho_repulsion_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p468_eph_ephrin_morpho_repulsion_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("EphEphrinMorphoRepulsionStudy", back_populates="metric_traces")
