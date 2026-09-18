"""Whole-Cell Metabolic Flux Simulation & Dynamic Genome-Scale Modeler Models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.connection import Base


class DBWholeCellModel(Base):
    __tablename__ = "whole_cell_metabolic_models"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organism_name = Column(String(255), nullable=False)
    genome_scale_model_id = Column(String(64), default="iML1515")
    total_reactions_count = Column(Integer, default=2712)
    total_metabolites_count = Column(Integer, default=1877)
    total_genes_count = Column(Integer, default=1515)
    biomass_objective_reaction = Column(String(128), default="BIOMASS_Ec_iML1515_core_75p37M")
    carbon_source = Column(String(64), default="GLUCOSE")
    optimal_growth_rate_hr1 = Column(Float, default=0.875)
    model_metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    flux_states = relationship("DBMetabolicFluxState", back_populates="model", cascade="all, delete-orphan")
    simulation_traces = relationship("DBKineticSimulationTrace", back_populates="model", cascade="all, delete-orphan")


class DBMetabolicFluxState(Base):
    __tablename__ = "metabolic_flux_states"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_id = Column(String(36), ForeignKey("whole_cell_metabolic_models.id", ondelete="CASCADE"), nullable=False)
    reaction_id = Column(String(64), nullable=False)
    reaction_name = Column(String(255), nullable=False)
    flux_value_mmol_gDW_hr = Column(Float, default=10.0)
    lower_bound = Column(Float, default=-1000.0)
    upper_bound = Column(Float, default=1000.0)
    subsystem = Column(String(128), default="GLYCOLYSIS")
    shadow_price = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    model = relationship("DBWholeCellModel", back_populates="flux_states")


class DBKineticSimulationTrace(Base):
    __tablename__ = "kinetic_simulation_traces"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_id = Column(String(36), ForeignKey("whole_cell_metabolic_models.id", ondelete="CASCADE"), nullable=False)
    time_point_hours = Column(Float, default=0.0)
    biomass_concentration_g_L = Column(Float, default=0.1)
    glucose_concentration_g_L = Column(Float, default=20.0)
    acetate_concentration_g_L = Column(Float, default=0.0)
    oxygen_uptake_rate = Column(Float, default=18.5)
    atp_yield_mol_per_mol_glucose = Column(Float, default=26.4)
    created_at = Column(DateTime, default=datetime.utcnow)

    model = relationship("DBWholeCellModel", back_populates="simulation_traces")
