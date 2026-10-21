"""SQLAlchemy models for Phase 578: Autonomous Xenobiotic Polyethylene Terephthalate (PET) Plastic Enzymatic Depolymerase Engineering & Micro-Solvation Energy Forecaster."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class XenobioticPetDepolymeraseStudy(Base):
    """Study record for Autonomous Xenobiotic Polyethylene Terephthalate (PET) Plastic Enzymatic Depolymerase Engineering & Micro-Solvation Energy Forecaster."""

    __tablename__ = "p578_xenobiotic_pet_depolymerase_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_enzyme = Column(String(150), nullable=False, default="Ideonella sakaiensis PETase Engineered Variant (Fast-PETase/LCC-ICCG)")
    substrate_type = Column(String(150), nullable=False, default="Post-Consumer Highly Crystalline Polyethylene Terephthalate (PET, 35% crystallinity)")
    catalytic_efficiency_kcat_km = Column(Float, nullable=False, default=142.5)
    melting_temperature_tm_celsius = Column(Float, nullable=False, default=78.2)
    solvation_free_energy_barrier_kcal = Column(Float, nullable=False, default=14.8)
    depolymerization_yield_percent = Column(Float, nullable=False, default=94.6)
    confidence_score = Column(Float, nullable=False, default=0.997)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("XenobioticPetDepolymeraseItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("XenobioticPetDepolymeraseMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class XenobioticPetDepolymeraseItemProfile(Base):
    """Detailed item profile for Autonomous Xenobiotic Polyethylene Terephthalate (PET) Plastic Enzymatic Depolymerase Engineering & Micro-Solvation Energy Forecaster."""

    __tablename__ = "p578_xenobiotic_pet_depolymerase_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p578_xenobiotic_pet_depolymerase_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Catalytic Subsite")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.8)
    significance_score = Column(Float, nullable=False, default=0.96)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("XenobioticPetDepolymeraseStudy", back_populates="item_profiles")


class XenobioticPetDepolymeraseMetricTrace(Base):
    """Metric trace for Autonomous Xenobiotic Polyethylene Terephthalate (PET) Plastic Enzymatic Depolymerase Engineering & Micro-Solvation Energy Forecaster."""

    __tablename__ = "p578_xenobiotic_pet_depolymerase_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p578_xenobiotic_pet_depolymerase_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.01)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("XenobioticPetDepolymeraseStudy", back_populates="metric_traces")
