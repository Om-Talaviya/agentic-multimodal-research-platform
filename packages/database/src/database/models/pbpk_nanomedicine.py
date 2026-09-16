"""
SQLAlchemy models for Nanomedicine Biodistribution & PBPK Simulator (Phase 60).
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship

from database.connection import Base


class DBNanomedicinePBPKSimulation(Base):
    """Represents a physiologically based pharmacokinetic (PBPK) nanomedicine simulation."""
    __tablename__ = "pbpk_simulations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    formulation_name = Column(String(128), nullable=False)  # LNP-mRNA, PLGA-PEG Micelle, Gold Nanostar
    carrier_type = Column(String(64), default="Lipid Nanoparticle (LNP)")
    hydrodynamic_diameter_nm = Column(Float, default=85.0)  # 20nm - 200nm
    zeta_potential_mv = Column(Float, default=-4.2)
    pegylation_density_pct = Column(Float, default=1.5)
    dose_mg_kg = Column(Float, default=1.0)
    tumor_epr_permeability_index = Column(Float, default=0.82)
    status = Column(String(32), default="COMPLETED")
    metadata_info = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    compartments = relationship("DBOrganCompartmentPK", back_populates="simulation", cascade="all, delete-orphan")
    clearance_pathways = relationship("DBNanoparticleClearancePathway", back_populates="simulation", cascade="all, delete-orphan")


class DBOrganCompartmentPK(Base):
    """Represents PK parameters in a specific physiological organ compartment."""
    __tablename__ = "pbpk_organ_compartments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    simulation_id = Column(String(36), ForeignKey("pbpk_simulations.id", ondelete="CASCADE"), nullable=False)
    organ_name = Column(String(64), nullable=False)  # Plasma, Liver, Spleen, Tumor, Kidneys, Heart, Lungs
    auc_ug_h_ml = Column(Float, nullable=False)
    cmax_ug_ml = Column(Float, nullable=False)
    tmax_hours = Column(Float, nullable=False)
    organ_to_plasma_ratio = Column(Float, default=1.0)
    fraction_of_dose_pct = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    simulation = relationship("DBNanomedicinePBPKSimulation", back_populates="compartments")


class DBNanoparticleClearancePathway(Base):
    """Represents elimination kinetics and MPS organ sequestration."""
    __tablename__ = "pbpk_clearance_pathways"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    simulation_id = Column(String(36), ForeignKey("pbpk_simulations.id", ondelete="CASCADE"), nullable=False)
    pathway_name = Column(String(64), nullable=False)  # Hepatic MPS/Kupffer, Splenic Red Pulp, Renal Filtration
    clearance_fraction_pct = Column(Float, nullable=False)
    half_life_hours = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    simulation = relationship("DBNanomedicinePBPKSimulation", back_populates="clearance_pathways")
