"""SQLAlchemy models for Phase 519: Autonomous Non-Equilibrium Active Matter Cytoskeletal Topological Defect Self-Propulsion Simulator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class ActiveMatterCytoskeletalNematicDefectStudy(Base):
    """Study record for Autonomous Non-Equilibrium Active Matter Cytoskeletal Topological Defect Self-Propulsion Simulator."""

    __tablename__ = "p519_active_matter_cytoskeletal_nematic_defect_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Microtubule-Kinesin Active Gel Nematic Liquid Crystal Layer at Oil-Water Interface")
    analytical_modality = Column(String(100), nullable=False, default="active-nematic-matter-dynamics")
    topological_defect_annihilation_rate_s_inv = Column(Float, nullable=False, default=0.45)
    active_turbulent_vortex_correlation_length_um = Column(Float, nullable=False, default=18.5)
    plus_half_defect_self_propulsion_velocity_um_per_s = Column(Float, nullable=False, default=4.8)
    atp_fuel_hydrolysis_energy_dissipation_rate_W_per_m3 = Column(Float, nullable=False, default=12.4)
    confidence_score = Column(Float, nullable=False, default=0.993)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("ActiveMatterCytoskeletalNematicDefectItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("ActiveMatterCytoskeletalNematicDefectMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class ActiveMatterCytoskeletalNematicDefectItemProfile(Base):
    """Detailed item profile for Autonomous Non-Equilibrium Active Matter Cytoskeletal Topological Defect Self-Propulsion Simulator."""

    __tablename__ = "p519_active_matter_cytoskeletal_nematic_defect_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p519_active_matter_cytoskeletal_nematic_defect_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("ActiveMatterCytoskeletalNematicDefectStudy", back_populates="item_profiles")


class ActiveMatterCytoskeletalNematicDefectMetricTrace(Base):
    """Metric trace for Autonomous Non-Equilibrium Active Matter Cytoskeletal Topological Defect Self-Propulsion Simulator."""

    __tablename__ = "p519_active_matter_cytoskeletal_nematic_defect_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p519_active_matter_cytoskeletal_nematic_defect_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("ActiveMatterCytoskeletalNematicDefectStudy", back_populates="metric_traces")
