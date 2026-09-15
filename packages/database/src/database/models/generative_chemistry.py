"""Database models for Autonomous De Novo Generative Molecule & Antibody Design (Phase 43)."""
from datetime import datetime, timezone
import uuid
from typing import List, Optional, Dict, Any

from sqlalchemy import String, Float, Integer, ForeignKey, Text, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
from database.models.memory import GUID, JSONType

class DBGenerativeMolecule(Base):
    __tablename__ = "generative_molecules"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id: Mapped[Optional[str]] = mapped_column(GUID(), ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True)
    project_id: Mapped[Optional[str]] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_protein: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., PCSK9, KRAS-G12D, EGFR
    smiles: Mapped[str] = mapped_column(Text, nullable=False)
    iupac_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    molecular_weight: Mapped[float] = mapped_column(Float, nullable=False)
    log_p: Mapped[float] = mapped_column(Float, nullable=False)
    h_bond_donors: Mapped[int] = mapped_column(Integer, default=2)
    h_bond_acceptors: Mapped[int] = mapped_column(Integer, default=5)
    rotatable_bonds: Mapped[int] = mapped_column(Integer, default=4)
    tpsa: Mapped[float] = mapped_column(Float, default=75.0)
    
    qed_score: Mapped[float] = mapped_column(Float, default=0.85)  # Quantitative Estimate of Drug-likeness (0-1)
    synthetic_accessibility: Mapped[float] = mapped_column(Float, default=2.8)  # SA Score (1 easy - 10 hard)
    predicted_binding_affinity: Mapped[float] = mapped_column(Float, default=-9.4)  # kcal/mol
    lipinski_violations: Mapped[int] = mapped_column(Integer, default=0)
    
    meta_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    admet_profile: Mapped[Optional["DBADMETProfile"]] = relationship("DBADMETProfile", back_populates="molecule", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_gen_mol_target", "target_protein"),
        Index("ix_gen_mol_affinity", "predicted_binding_affinity"),
    )

class DBADMETProfile(Base):
    __tablename__ = "admet_profiles"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    molecule_id: Mapped[str] = mapped_column(GUID(), ForeignKey("generative_molecules.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    human_intestinal_absorption: Mapped[float] = mapped_column(Float, default=92.5)  # percentage
    blood_brain_barrier_permeability: Mapped[float] = mapped_column(Float, default=0.45)  # logBB
    cyp3a4_inhibition_risk: Mapped[bool] = mapped_column(Boolean, default=False)
    cyp2d6_inhibition_risk: Mapped[bool] = mapped_column(Boolean, default=False)
    herg_cardiotoxicity_risk: Mapped[bool] = mapped_column(Boolean, default=False)
    plasma_protein_binding: Mapped[float] = mapped_column(Float, default=88.0)  # percentage
    half_life_hours: Mapped[float] = mapped_column(Float, default=6.5)
    
    meta_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    molecule: Mapped["DBGenerativeMolecule"] = relationship("DBGenerativeMolecule", back_populates="admet_profile")

class DBAntibodyCandidate(Base):
    __tablename__ = "antibody_candidates"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id: Mapped[Optional[str]] = mapped_column(GUID(), ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True)
    project_id: Mapped[Optional[str]] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    
    variant_name: Mapped[str] = mapped_column(String(255), nullable=False)
    antigen_target: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., PD-L1, CLDN18.2, HER2
    heavy_chain_seq: Mapped[str] = mapped_column(Text, nullable=False)
    light_chain_seq: Mapped[str] = mapped_column(Text, nullable=False)
    cdr_h3_sequence: Mapped[str] = mapped_column(String(100), nullable=False)  # engineered loop
    
    kd_affinity_nm: Mapped[float] = mapped_column(Float, nullable=False)  # nanomolar binding affinity
    melting_temperature_c: Mapped[float] = mapped_column(Float, default=74.5)  # thermal stability Tm
    humanness_score: Mapped[float] = mapped_column(Float, default=0.92)  # 0 to 1
    sequence_liabilities_count: Mapped[int] = mapped_column(Integer, default=0)  # deamidation/isomerization motifs
    
    meta_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_ab_antigen", "antigen_target"),
        Index("ix_ab_kd", "kd_affinity_nm"),
    )
