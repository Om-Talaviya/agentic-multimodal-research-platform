"""
SQLAlchemy database models for Phase 108: Organ-on-a-Chip Microphysiological Fluidic Dynamics.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID

class DBOrganOnChipSimulation(Base):
    __tablename__ = "organ_chip_simulations"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=True, index=True)
    chip_name = Column(String(255), nullable=False, index=True)
    organ_type = Column(String(100), default="BLOOD_BRAIN_BARRIER", index=True)
    fluid_viscosity_cp = Column(Float, default=1.0)
    perfusion_flow_rate_ul_min = Column(Float, default=30.0)
    shear_stress_dyn_cm2 = Column(Float, default=5.2)
    endothelial_barrier_integrity_teer = Column(Float, default=1250.0)
    metadata_json = Column(JSON, nullable=True)
    status = Column(String(50), default="COMPLETED")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    channels = relationship("DBMicrofluidicChannel", back_populates="simulation", cascade="all, delete-orphan")
    shear_profiles = relationship("DBShearStressProfile", back_populates="simulation", cascade="all, delete-orphan")

class DBMicrofluidicChannel(Base):
    __tablename__ = "microfluidic_channels"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    simulation_id = Column(GUID(), ForeignKey("organ_chip_simulations.id", ondelete="CASCADE"), nullable=False, index=True)
    channel_name = Column(String(100), nullable=False, index=True)
    width_um = Column(Float, default=400.0)
    height_um = Column(Float, default=100.0)
    length_mm = Column(Float, default=20.0)
    flow_velocity_mm_s = Column(Float, default=2.5)
    reynolds_number = Column(Float, default=0.08)
    created_at = Column(DateTime, default=datetime.utcnow)

    simulation = relationship("DBOrganOnChipSimulation", back_populates="channels")

class DBShearStressProfile(Base):
    __tablename__ = "shear_stress_profiles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    simulation_id = Column(GUID(), ForeignKey("organ_chip_simulations.id", ondelete="CASCADE"), nullable=False, index=True)
    axial_position_mm = Column(Float, nullable=False)
    wall_shear_stress = Column(Float, default=5.0)
    drug_permeation_pct = Column(Float, default=12.5)
    tight_junction_expression = Column(Float, default=95.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    simulation = relationship("DBOrganOnChipSimulation", back_populates="shear_profiles")
