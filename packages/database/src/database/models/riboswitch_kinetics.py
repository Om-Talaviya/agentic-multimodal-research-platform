"""
Phase 134: Non-Coding RNA Riboswitch Kinetic Switch Simulator & Aptamer Free-Energy Folding Database Models.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID, JSON


class DBRiboswitchCircuit(Base):
    __tablename__ = "riboswitch_circuits"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID, nullable=True, index=True)
    circuit_name = Column(String(255), nullable=False, index=True)
    target_ligand = Column(String(255), nullable=False)
    rna_sequence = Column(Text, nullable=False)
    aptamer_class = Column(String(100), nullable=False, default="SAM-I")
    expression_platform_type = Column(String(100), nullable=False, default="Rho-Independent Terminator")
    dynamic_range_fold = Column(Float, nullable=False, default=8.5)
    switching_free_energy_delta_g = Column(Float, nullable=False, default=-14.2)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    secondary_structures = relationship(
        "DBRNALoopSecondaryStructure",
        back_populates="circuit",
        cascade="all, delete-orphan",
    )
    ligand_kinetics = relationship(
        "DBLigandKineticsProfile",
        back_populates="circuit",
        cascade="all, delete-orphan",
    )


class DBRNALoopSecondaryStructure(Base):
    __tablename__ = "rna_loop_secondary_structures"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    circuit_id = Column(GUID, ForeignKey("riboswitch_circuits.id", ondelete="CASCADE"), nullable=False, index=True)
    state_name = Column(String(100), nullable=False)  # "Apo (OFF)", "Holo (ON)"
    dot_bracket_notation = Column(Text, nullable=False)
    minimum_free_energy_mfe = Column(Float, nullable=False)
    ensemble_defect_percent = Column(Float, nullable=False, default=4.2)
    pseudoknot_present = Column(String(10), nullable=False, default="NO")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    circuit = relationship("DBRiboswitchCircuit", back_populates="secondary_structures")


class DBLigandKineticsProfile(Base):
    __tablename__ = "ligand_kinetics_profiles"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    circuit_id = Column(GUID, ForeignKey("riboswitch_circuits.id", ondelete="CASCADE"), nullable=False, index=True)
    association_rate_k_on = Column(Float, nullable=False)  # M^-1 s^-1
    dissociation_rate_k_off = Column(Float, nullable=False)  # s^-1
    equilibrium_dissociation_constant_kd_nm = Column(Float, nullable=False)  # nM
    cotranscriptional_folding_window_nt = Column(Integer, nullable=False, default=45)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    circuit = relationship("DBRiboswitchCircuit", back_populates="ligand_kinetics")
