"""Phase 158: Multi-Target Bispecific & Trispecific T-Cell Engager Models."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBMultispecificTCellEngagerStudy(Base):
    """Multi-specific T-cell engager (BiTE/TriTE) synapse structural modeling study."""

    __tablename__ = "multispecific_tcell_engager_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    construct_name = Column(String(255), nullable=False)
    modality_format = Column(String(64), default="TriTE (Trispecific T-Cell Engager)")
    primary_tumor_antigen = Column(String(120), default="EGFR / HER2 Dual-Target")
    tcell_activation_arm = Column(String(64), default="Anti-CD3e (UCHT1-Derived)")
    synaptic_cleft_distance_a = Column(Float, default=0.0)
    cytolytic_potency_ec50_pm = Column(Float, default=0.0)
    perforin_granzyme_flux = Column(Float, default=0.0)
    crs_cytokine_risk_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    binding_domains = relationship("DBTargetBindingDomainGeometry", back_populates="study", cascade="all, delete-orphan")
    synapse_profiles = relationship("DBSynapticDistanceProfile", back_populates="study", cascade="all, delete-orphan")


class DBTargetBindingDomainGeometry(Base):
    """Specific scFv / VHH binding arm coordinate and affinity."""

    __tablename__ = "target_binding_domain_geometries"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("multispecific_tcell_engager_studies.id", ondelete="CASCADE"), nullable=False)
    arm_designation = Column(String(64), nullable=False)
    target_epitope = Column(String(120), nullable=False)
    kd_affinity_nM = Column(Float, nullable=False)
    arm_length_angstrom = Column(Float, nullable=False)
    rotational_flexibility_deg = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBMultispecificTCellEngagerStudy", back_populates="binding_domains")


class DBSynapticDistanceProfile(Base):
    """Immunological synapse membrane-to-membrane geometry and cytotoxicity."""

    __tablename__ = "synaptic_distance_profiles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("multispecific_tcell_engager_studies.id", ondelete="CASCADE"), nullable=False)
    intermembrane_distance_nm = Column(Float, nullable=False)
    synapse_maturation_time_min = Column(Float, nullable=False)
    lytic_granule_polarization_pct = Column(Float, nullable=False)
    tumor_lysis_percentage = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBMultispecificTCellEngagerStudy", back_populates="synapse_profiles")
