import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base

class DBBiotherapeuticConstruct(Base):
    __tablename__ = "biotherapeutic_constructs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    construct_name = Column(String(255), nullable=False)
    modality = Column(String(100), nullable=False, default="mAb")  # mAb, Bispecific, Tri-specific, ADC, Fusion Protein
    heavy_chain_sequence = Column(Text, nullable=False)
    light_chain_sequence = Column(Text, nullable=True)
    melting_temp_tm1_celsius = Column(Float, nullable=False, default=71.5)  # CH2 / Fab unfolding Tm
    melting_temp_tm2_celsius = Column(Float, nullable=False, default=82.4)  # CH3 unfolding Tm
    aggregation_propensity_score = Column(Float, nullable=False, default=0.18)  # SAP score (0.0 - 1.0, lower is better)
    colloidal_stability_kd = Column(Float, nullable=False, default=-5.2)  # DLS interaction parameter k_D (mL/g)
    diffusion_interaction_parameter_b22 = Column(Float, nullable=False, default=1.8e-4)  # B22 (mol*mL/g^2)
    shelf_life_months_at_4c = Column(Float, nullable=False, default=24.0)
    properties = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    hydrophobic_patches = relationship("DBHydrophobicPatch", back_populates="construct", cascade="all, delete-orphan")
    excipient_screens = relationship("DBFormulationExcipientScreen", back_populates="construct", cascade="all, delete-orphan")

class DBHydrophobicPatch(Base):
    __tablename__ = "biotherapeutic_hydrophobic_patches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    construct_id = Column(String(36), ForeignKey("biotherapeutic_constructs.id", ondelete="CASCADE"), nullable=False)
    patch_identifier = Column(String(100), nullable=False)  # CDR-H3 Patch, CH2 Loop Patch
    surface_area_angstrom2 = Column(Float, nullable=False)  # Area in A^2
    average_hydrophobicity_score = Column(Float, nullable=False)  # Kyte-Doolittle scale
    residue_span = Column(String(100), nullable=False)  # e.g. "HC: 98-106 (W-Y-F-L)"
    aggregation_risk_level = Column(String(50), nullable=False, default="LOW")  # HIGH, MODERATE, LOW
    created_at = Column(DateTime, default=datetime.utcnow)

    construct = relationship("DBBiotherapeuticConstruct", back_populates="hydrophobic_patches")

class DBFormulationExcipientScreen(Base):
    __tablename__ = "biotherapeutic_excipient_screens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    construct_id = Column(String(36), ForeignKey("biotherapeutic_constructs.id", ondelete="CASCADE"), nullable=False)
    buffer_type = Column(String(100), nullable=False, default="Histidine")  # Histidine, Citrate, Acetate, Phosphate
    ph = Column(Float, nullable=False, default=6.0)
    surfactant = Column(String(100), nullable=False, default="Polysorbate 80")  # PS20, PS80, Poloxamer 188
    tonicity_agent = Column(String(100), nullable=False, default="Sucrose")  # Sucrose, Trehalose, Arginine-HCl, NaCl
    monomer_retention_pct_at_40c = Column(Float, nullable=False, default=96.8)  # % SEC monomer after 4 weeks at 40C
    created_at = Column(DateTime, default=datetime.utcnow)

    construct = relationship("DBBiotherapeuticConstruct", back_populates="excipient_screens")
