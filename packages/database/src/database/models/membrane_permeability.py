"""In-Silico Membrane Permeability & PAMPA QSAR Models (Phase 140)."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import JSON, GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBPAMPAPermeabilityStudy(Base):
    """PAMPA artificial membrane permeability assay simulation."""

    __tablename__ = "pampa_permeability_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    molecule_name = Column(String(255), nullable=False)
    smiles = Column(String(1000), nullable=False)
    molecular_weight = Column(Float, nullable=False)
    logp = Column(Float, nullable=False)
    tpsa = Column(Float, nullable=False)
    papp_cm_per_s = Column(Float, default=0.0)
    permeability_class = Column(String(50), default="Moderate")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    diffusivity_records = relationship("DBMembraneDiffusivityRecord", back_populates="study", cascade="all, delete-orphan")
    qsar_profiles = relationship("DBPermeabilityQSARProfile", back_populates="study", cascade="all, delete-orphan")


class DBMembraneDiffusivityRecord(Base):
    """Lipid bilayer depth-dependent diffusivity profile."""

    __tablename__ = "membrane_diffusivity_records"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("pampa_permeability_studies.id", ondelete="CASCADE"), nullable=False)
    bilayer_depth_angstrom = Column(Float, nullable=False)
    free_energy_barrier_kcal_mol = Column(Float, nullable=False)
    local_diffusion_coefficient = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBPAMPAPermeabilityStudy", back_populates="diffusivity_records")


class DBPermeabilityQSARProfile(Base):
    """QSAR feature weights and machine learning descriptor record."""

    __tablename__ = "permeability_qsar_profiles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("pampa_permeability_studies.id", ondelete="CASCADE"), nullable=False)
    h_bond_donors = Column(Integer, default=0)
    h_bond_acceptors = Column(Integer, default=0)
    rotatable_bonds = Column(Integer, default=0)
    predicted_pampa_score = Column(Float, default=0.0)
    is_blood_brain_barrier_permeable = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBPAMPAPermeabilityStudy", back_populates="qsar_profiles")
