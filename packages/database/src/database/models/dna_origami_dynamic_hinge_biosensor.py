"""SQLAlchemy models for Phase 435: Autonomous Reconfigurable DNA Origami Dynamic Hinge Compliant Nano-Actuator Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class DnaOrigamiDynamicHingeStudy(Base):
    """Study record for Autonomous Reconfigurable DNA Origami Dynamic Hinge Compliant Nano-Actuator Engine."""

    __tablename__ = "p435_dna_origami_dynamic_hinge_biosensor_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Hexagonal Bundle DNA Origami Nano-Hinge with Fluorophore/Quencher FRET Pair")
    analytical_modality = Column(String(100), nullable=False, default="dna-origami-hinge")
    hinge_flexibility_angle_deg = Column(Float, nullable=False, default=62.4)
    fret_efficiency_dynamic_ratio = Column(Float, nullable=False, default=0.865)
    folding_yield_percentage = Column(Float, nullable=False, default=91.2)
    magnesium_stabilization_mM = Column(Float, nullable=False, default=12.5)
    confidence_score = Column(Float, nullable=False, default=0.988)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("DnaOrigamiDynamicHingeItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("DnaOrigamiDynamicHingeMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class DnaOrigamiDynamicHingeItemProfile(Base):
    """Detailed item profile for Autonomous Reconfigurable DNA Origami Dynamic Hinge Compliant Nano-Actuator Engine."""

    __tablename__ = "p435_dna_origami_dynamic_hinge_biosensor_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p435_dna_origami_dynamic_hinge_biosensor_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DnaOrigamiDynamicHingeStudy", back_populates="item_profiles")


class DnaOrigamiDynamicHingeMetricTrace(Base):
    """Metric trace for Autonomous Reconfigurable DNA Origami Dynamic Hinge Compliant Nano-Actuator Engine."""

    __tablename__ = "p435_dna_origami_dynamic_hinge_biosensor_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p435_dna_origami_dynamic_hinge_biosensor_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DnaOrigamiDynamicHingeStudy", back_populates="metric_traces")
