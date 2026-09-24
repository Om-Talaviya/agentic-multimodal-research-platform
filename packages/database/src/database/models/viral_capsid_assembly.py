"""Phase 151: AAV Viral Capsid Thermodynamic Self-Assembly Models."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBViralCapsidAssemblyStudy(Base):
    """AAV viral capsid icosahedral self-assembly study."""

    __tablename__ = "viral_capsid_assembly_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    serotype_name = Column(String(120), nullable=False)
    triangulation_number = Column(String(32), default="T=1 (60-mer)")
    vp_stoichiometry_ratio = Column(String(64), default="1:1:10 (VP1:VP2:VP3)")
    assembly_yield_percent = Column(Float, default=0.0)
    gibbs_free_energy_kcal_mol = Column(Float, default=0.0)
    critical_nucleus_size = Column(Integer, default=5)
    full_empty_capsid_ratio = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    interfaces = relationship("DBCapsomerInterfaceEnergy", back_populates="study", cascade="all, delete-orphan")
    trajectories = relationship("DBCapsidThermodynamicTrajectory", back_populates="study", cascade="all, delete-orphan")


class DBCapsomerInterfaceEnergy(Base):
    """Subunit interface binding thermodynamics (2-fold, 3-fold, 5-fold axes)."""

    __tablename__ = "capsomer_interface_energies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("viral_capsid_assembly_studies.id", ondelete="CASCADE"), nullable=False)
    symmetry_axis = Column(String(64), nullable=False)
    delta_g_binding_kcal_mol = Column(Float, nullable=False)
    buried_surface_area_a2 = Column(Float, nullable=False)
    hydrogen_bonds_count = Column(Integer, nullable=False)
    salt_bridges_count = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBViralCapsidAssemblyStudy", back_populates="interfaces")


class DBCapsidThermodynamicTrajectory(Base):
    """Kinetic intermediate step during icosahedral capsid nucleation."""

    __tablename__ = "capsid_thermodynamic_trajectories"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("viral_capsid_assembly_studies.id", ondelete="CASCADE"), nullable=False)
    oligomer_size = Column(Integer, nullable=False)
    forward_rate_k_on = Column(Float, nullable=False)
    reverse_rate_k_off = Column(Float, nullable=False)
    fraction_assembled = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBViralCapsidAssemblyStudy", back_populates="trajectories")
