"""Autonomous Bio-Molecular Structure & Protein Folding Database Models (Phase 38)."""

import uuid
from datetime import UTC, datetime
from typing import Optional
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID, JSONType


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBMolecularStructure(Base):
    """3D Bio-molecular protein structure record derived from AlphaFold3, ESMFold, or PDB."""

    __tablename__ = "molecular_structures"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(GUID(), ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True, index=True)
    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)

    uniprot_id = Column(String(50), nullable=False, index=True)  # e.g., Q9BYF1 (PCSK9), Q99250 (Cas9)
    gene_name = Column(String(100), nullable=False)
    organism = Column(String(150), nullable=False, default="Homo sapiens")
    sequence = Column(Text, nullable=False)
    mean_plddt_score = Column(Float, nullable=False, default=88.5)  # 0.0 to 100.0
    resolution_angstrom = Column(Float, nullable=True, default=1.85)
    structure_source = Column(String(50), nullable=False, default="AlphaFold3")  # AlphaFold3, ESMFold, PDB_Experimental
    pdb_coordinate_data = Column(Text, nullable=False)
    secondary_structure_summary = Column(JSONType, nullable=False, default=dict)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    binding_pockets = relationship(
        "DBBindingPocket",
        back_populates="structure",
        cascade="all, delete-orphan",
        order_by="DBBindingPocket.pocket_index",
    )
    docking_poses = relationship(
        "DBDockingPose",
        back_populates="structure",
        cascade="all, delete-orphan",
    )
    mutations = relationship(
        "DBMutationStability",
        back_populates="structure",
        cascade="all, delete-orphan",
        order_by="DBMutationStability.position",
    )


class DBBindingPocket(Base):
    """Predicted catalytic cleft or small molecule binding pocket on molecular surface."""

    __tablename__ = "binding_pockets"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    structure_id = Column(GUID(), ForeignKey("molecular_structures.id", ondelete="CASCADE"), nullable=False, index=True)

    pocket_index = Column(Integer, nullable=False)  # 1, 2, 3...
    druggability_score = Column(Float, nullable=False, default=0.82)  # 0.0 to 1.0
    volume_cubic_angstrom = Column(Float, nullable=False, default=650.0)
    surface_area_angstrom2 = Column(Float, nullable=False, default=420.0)
    key_residues_json = Column(JSONType, nullable=False, default=list)  # e.g., ["ASP374", "PHE379", "LEU380"]
    center_coordinates_json = Column(JSONType, nullable=False, default=dict)  # {"x": 12.4, "y": -4.2, "z": 38.1}

    # Relationships
    structure = relationship("DBMolecularStructure", back_populates="binding_pockets")
    docking_poses = relationship("DBDockingPose", back_populates="pocket", cascade="all, delete-orphan")


class DBDockingPose(Base):
    """Small molecule ligand or peptide docking pose within a predicted binding pocket."""

    __tablename__ = "docking_poses"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    structure_id = Column(GUID(), ForeignKey("molecular_structures.id", ondelete="CASCADE"), nullable=False, index=True)
    pocket_id = Column(GUID(), ForeignKey("binding_pockets.id", ondelete="CASCADE"), nullable=False, index=True)

    ligand_name = Column(String(200), nullable=False)  # e.g., "Evolocumab Mimetic Small Molecule"
    binding_affinity_kcal_mol = Column(Float, nullable=False, default=-9.4)  # Negative is more favorable
    rmsd_angstrom = Column(Float, nullable=False, default=1.12)
    hydrogen_bonds_count = Column(Integer, nullable=False, default=4)
    pi_stacking_interactions = Column(Integer, nullable=False, default=2)
    pose_coordinates_json = Column(JSONType, nullable=False, default=dict)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    structure = relationship("DBMolecularStructure", back_populates="docking_poses")
    pocket = relationship("DBBindingPocket", back_populates="docking_poses")


class DBMutationStability(Base):
    """In-silico mutational scanning stability change (Delta Delta G in kcal/mol)."""

    __tablename__ = "mutation_stabilities"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    structure_id = Column(GUID(), ForeignKey("molecular_structures.id", ondelete="CASCADE"), nullable=False, index=True)

    wildtype_residue = Column(String(10), nullable=False)  # e.g., "D" (Asp)
    position = Column(Integer, nullable=False)  # e.g., 374
    mutant_residue = Column(String(10), nullable=False)  # e.g., "Y" (Tyr)
    delta_delta_g_kcal_mol = Column(Float, nullable=False, default=-2.4)  # <0 stabilizing, >0 destabilizing
    stability_verdict = Column(String(50), nullable=False, default="stabilizing")  # stabilizing, destabilizing, neutral
    pathogenicity_score = Column(Float, nullable=False, default=0.78)  # 0.0 (benign) to 1.0 (pathogenic)

    # Relationships
    structure = relationship("DBMolecularStructure", back_populates="mutations")
