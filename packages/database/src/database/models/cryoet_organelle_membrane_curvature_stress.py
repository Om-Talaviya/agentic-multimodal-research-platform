"""SQLAlchemy models for Phase 536: Autonomous In-Situ Cryo-ET Endoplasmic Reticulum-Mitochondria Membrane Curvature Elastic Stress Profiler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CryoetOrganelleMembraneCurvatureStressStudy(Base):
    """Study record for Autonomous In-Situ Cryo-ET Endoplasmic Reticulum-Mitochondria Membrane Curvature Elastic Stress Profiler."""

    __tablename__ = "p536_cryoet_organelle_membrane_curvature_stress_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Vitrified Primary Murine Hepatocyte Lamella showing In-Situ MAM (Mitochondria-Associated ER Membrane) Junctions")
    analytical_modality = Column(String(100), nullable=False, default="cryoet-organelle-membrane-stress")
    membrane_bending_modulus_kbT = Column(Float, nullable=False, default=22.5)
    mam_intermembrane_contact_distance_nm = Column(Float, nullable=False, default=14.2)
    principal_curvature_radius_nm = Column(Float, nullable=False, default=18.4)
    lipid_packing_defect_density_per_nm2 = Column(Float, nullable=False, default=0.038)
    confidence_score = Column(Float, nullable=False, default=0.993)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CryoetOrganelleMembraneCurvatureStressItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("CryoetOrganelleMembraneCurvatureStressMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class CryoetOrganelleMembraneCurvatureStressItemProfile(Base):
    """Detailed item profile for Autonomous In-Situ Cryo-ET Endoplasmic Reticulum-Mitochondria Membrane Curvature Elastic Stress Profiler."""

    __tablename__ = "p536_cryoet_organelle_membrane_curvature_stress_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p536_cryoet_organelle_membrane_curvature_stress_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CryoetOrganelleMembraneCurvatureStressStudy", back_populates="item_profiles")


class CryoetOrganelleMembraneCurvatureStressMetricTrace(Base):
    """Metric trace for Autonomous In-Situ Cryo-ET Endoplasmic Reticulum-Mitochondria Membrane Curvature Elastic Stress Profiler."""

    __tablename__ = "p536_cryoet_organelle_membrane_curvature_stress_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p536_cryoet_organelle_membrane_curvature_stress_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CryoetOrganelleMembraneCurvatureStressStudy", back_populates="metric_traces")
