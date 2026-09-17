import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base

class DBCircuitBurdenSimulation(Base):
    __tablename__ = "gene_circuit_burden_simulations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    circuit_name = Column(String(255), nullable=False)
    host_organism = Column(String(100), nullable=False, default="E. coli K-12")  # E. coli, S. cerevisiae, CHO
    promoter_strength_rpum = Column(Float, nullable=False, default=1250.0)  # Relative Promoter Units
    ribosome_allocation_pct = Column(Float, nullable=False, default=18.5)  # % of cellular ribosomes hijacked
    growth_rate_penalty_pct = Column(Float, nullable=False, default=14.2)  # % decrease in specific growth rate
    evolutionary_half_life_generations = Column(Float, nullable=False, default=42.0)  # Generations before 50% non-functional
    circuit_failure_mode = Column(String(100), nullable=False, default="IS Insertion")  # IS Element, Point Mutation, Silencing
    properties = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    capacity_models = relationship("DBHostCapacityModel", back_populates="simulation", cascade="all, delete-orphan")

class DBHostCapacityModel(Base):
    __tablename__ = "host_capacity_models"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    simulation_id = Column(String(36), ForeignKey("gene_circuit_burden_simulations.id", ondelete="CASCADE"), nullable=False)
    free_ribosome_pool_fraction = Column(Float, nullable=False, default=0.72)
    atp_drain_flux_mmol_gdw_h = Column(Float, nullable=False, default=2.8)
    chaperone_load_index = Column(Float, nullable=False, default=0.35)
    metabolic_burden_status = Column(String(50), nullable=False, default="BALANCED")  # OPTIMAL, BALANCED, SEVERE_BURDEN
    created_at = Column(DateTime, default=datetime.utcnow)

    simulation = relationship("DBCircuitBurdenSimulation", back_populates="capacity_models")
