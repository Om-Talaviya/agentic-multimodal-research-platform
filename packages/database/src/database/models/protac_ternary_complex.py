"""Phase 156: PROTAC Ternary Complex Degradation Kinetics Models."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBPROTACTernaryComplexStudy(Base):
    """PROTAC ternary complex stability and proteasomal degradation kinetics study."""

    __tablename__ = "protac_ternary_complex_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    protac_compound_name = Column(String(255), nullable=False)
    target_protein_name = Column(String(120), nullable=False)
    e3_ligase_name = Column(String(64), default="CRBN (Cereblon)")
    linker_type = Column(String(120), default="PEG4-Alkyne Flexible Linker")
    cooperativity_alpha = Column(Float, default=1.0)
    dc50_nM = Column(Float, default=0.0)
    dmax_percent = Column(Float, default=0.0)
    hook_effect_threshold_uM = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    e3_profiles = relationship("DBE3LigaseBindingProfile", back_populates="study", cascade="all, delete-orphan")
    degradation_points = relationship("DBProteinDegradationKineticPoint", back_populates="study", cascade="all, delete-orphan")


class DBE3LigaseBindingProfile(Base):
    """Binding affinity (Kd) to target and E3 ligase binding domains."""

    __tablename__ = "e3_ligase_binding_profiles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("protac_ternary_complex_studies.id", ondelete="CASCADE"), nullable=False)
    domain_type = Column(String(64), nullable=False)
    kd_binary_nM = Column(Float, nullable=False)
    kd_ternary_nM = Column(Float, nullable=False)
    delta_g_formation_kcal_mol = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBPROTACTernaryComplexStudy", back_populates="e3_profiles")


class DBProteinDegradationKineticPoint(Base):
    """Concentration vs target degradation fraction point mapping the Hook effect."""

    __tablename__ = "protein_degradation_kinetic_points"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("protac_ternary_complex_studies.id", ondelete="CASCADE"), nullable=False)
    protac_dose_nM = Column(Float, nullable=False)
    ternary_fraction = Column(Float, nullable=False)
    degradation_rate_pct = Column(Float, nullable=False)
    ubiquitination_flux = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBPROTACTernaryComplexStudy", back_populates="degradation_points")
