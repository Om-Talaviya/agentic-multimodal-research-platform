"""Cryo-EM Protein Flexible Backbone Ensemble Database Models (Phase 97)."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID


class DBCryoEmEnsemble(Base):
    __tablename__ = "cryo_em_ensembles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    target_protein = Column(String(255), nullable=False)  # e.g., GLP-1R / G-protein Complex, Spike Glycoprotein
    pdb_reference_id = Column(String(50), nullable=False)
    density_map_resolution_angstrom = Column(Float, default=2.65, nullable=False)
    latent_space_dimensions = Column(Integer, default=3, nullable=False)
    total_conformational_states = Column(Integer, default=4, nullable=False)
    flexibility_rmsd_angstrom = Column(Float, default=3.82, nullable=False)
    ensemble_metadata = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    states = relationship("DBCryoConformationalState", back_populates="ensemble", cascade="all, delete-orphan")
    transitions = relationship("DBFreeEnergyTransition", back_populates="ensemble", cascade="all, delete-orphan")


class DBCryoConformationalState(Base):
    __tablename__ = "cryo_conformational_states"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    ensemble_id = Column(GUID(), ForeignKey("cryo_em_ensembles.id", ondelete="CASCADE"), nullable=False, index=True)
    state_label = Column(String(100), nullable=False)  # Open (Active), Closed (Inactive), Intermediate 1, Intermediate 2
    population_percentage = Column(Float, nullable=False)  # e.g., 42.5%
    relative_free_energy_kcal_mol = Column(Float, nullable=False)  # e.g., 0.0, 1.25, 2.40
    backbone_rmsd_to_reference = Column(Float, nullable=False)
    binding_pocket_volume_angstrom3 = Column(Float, default=740.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    ensemble = relationship("DBCryoEmEnsemble", back_populates="states")


class DBFreeEnergyTransition(Base):
    __tablename__ = "cryo_free_energy_transitions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    ensemble_id = Column(GUID(), ForeignKey("cryo_em_ensembles.id", ondelete="CASCADE"), nullable=False, index=True)
    from_state = Column(String(100), nullable=False)
    to_state = Column(String(100), nullable=False)
    energy_barrier_kcal_mol = Column(Float, nullable=False)
    transition_rate_per_sec = Column(Float, default=4.5e4, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    ensemble = relationship("DBCryoEmEnsemble", back_populates="transitions")
