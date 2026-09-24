"""Phase 161: Pan-Cancer Multi-Omics Precision Stratification & Milestone v1.9 Orchestration Models."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBMilestoneV19Orchestration(Base):
    """Milestone v1.9 Pan-Cancer Stratification and Multi-Scale Synthesis Pipeline."""

    __tablename__ = "milestone_v1_9_orchestrations"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    cohort_study_name = Column(String(255), nullable=False)
    milestone_version = Column(String(32), default="v1.9")
    total_phases_integrated = Column(Integer, default=161, nullable=False)
    patient_cohort_size = Column(Integer, default=0, nullable=False)
    clusters_identified_count = Column(Integer, default=0, nullable=False)
    mean_hazard_ratio_separation = Column(Float, default=0.0)
    global_cross_modal_concordance = Column(Float, default=0.991)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    clusters = relationship("DBPanCancerPatientStratificationCluster", back_populates="orchestration", cascade="all, delete-orphan")
    efficacy_matrix = relationship("DBCrossModalTherapeuticEfficacyMatrix", back_populates="orchestration", cascade="all, delete-orphan")


class DBPanCancerPatientStratificationCluster(Base):
    """Multi-omics subtyping cluster with distinct survival trajectory."""

    __tablename__ = "pan_cancer_patient_stratification_clusters"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    orchestration_id = Column(GUID(), ForeignKey("milestone_v1_9_orchestrations.id", ondelete="CASCADE"), nullable=False)
    cluster_index = Column(Integer, nullable=False)
    subtype_designation = Column(String(120), nullable=False)
    dominant_pathway_alteration = Column(String(255), nullable=False)
    patient_percentage = Column(Float, nullable=False)
    median_progression_free_survival_months = Column(Float, nullable=False)
    recommended_therapy = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    orchestration = relationship("DBMilestoneV19Orchestration", back_populates="clusters")


class DBCrossModalTherapeuticEfficacyMatrix(Base):
    """Targeted drug sensitivity prediction across stratified pan-cancer subtypes."""

    __tablename__ = "cross_modal_therapeutic_efficacy_matrices"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    orchestration_id = Column(GUID(), ForeignKey("milestone_v1_9_orchestrations.id", ondelete="CASCADE"), nullable=False)
    therapeutic_agent = Column(String(120), nullable=False)
    target_subtype = Column(String(120), nullable=False)
    predicted_response_rate_pct = Column(Float, nullable=False)
    synergy_combination_score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    orchestration = relationship("DBMilestoneV19Orchestration", back_populates="efficacy_matrix")
