"""Pharmacokinetic-Pharmacodynamic (PK/PD) Database Models (Phase 99)."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID


class DBPkPdSimulation(Base):
    __tablename__ = "pkpd_simulations"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    drug_name = Column(String(255), nullable=False)
    route_of_administration = Column(String(50), default="ORAL", nullable=False)  # ORAL, IV_BOLUS, IV_INFUSION, SUBCUTANEOUS
    dose_mg = Column(Float, nullable=False)
    dosing_interval_hours = Column(Float, default=24.0, nullable=False)
    cmax_ug_ml = Column(Float, nullable=False)
    tmax_hours = Column(Float, nullable=False)
    auc_inf_ug_hr_ml = Column(Float, nullable=False)
    elimination_half_life_hours = Column(Float, nullable=False)
    clearance_l_per_hr = Column(Float, nullable=False)
    volume_distribution_l = Column(Float, nullable=False)
    therapeutic_window_compliance = Column(String(50), default="OPTIMAL", nullable=False)  # OPTIMAL, SUBTHERAPEUTIC, TOXIC_EXCURSION
    simulation_metadata = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    tissue_concentrations = relationship("DBTissueConcentration", back_populates="simulation", cascade="all, delete-orphan")
    pd_effects = relationship("DBPharmacodynamicEffect", back_populates="simulation", cascade="all, delete-orphan")


class DBTissueConcentration(Base):
    __tablename__ = "pkpd_tissue_concentrations"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    simulation_id = Column(GUID(), ForeignKey("pkpd_simulations.id", ondelete="CASCADE"), nullable=False, index=True)
    tissue_organ = Column(String(100), nullable=False)  # Plasma, Liver, Kidney, Brain, Heart, Tumor
    kp_partition_coefficient = Column(Float, default=1.2, nullable=False)
    cmax_tissue_ug_g = Column(Float, nullable=False)
    auc_tissue_ug_hr_g = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    simulation = relationship("DBPkPdSimulation", back_populates="tissue_concentrations")


class DBPharmacodynamicEffect(Base):
    __tablename__ = "pkpd_effects"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    simulation_id = Column(GUID(), ForeignKey("pkpd_simulations.id", ondelete="CASCADE"), nullable=False, index=True)
    biomarker_name = Column(String(100), nullable=False)  # Target Receptor Occupancy %, Tumor Volume Reduction %, Blood Pressure Change
    emax_percent = Column(Float, default=95.0, nullable=False)
    ec50_ug_ml = Column(Float, default=0.45, nullable=False)
    hill_coefficient = Column(Float, default=1.8, nullable=False)
    max_effect_observed = Column(Float, nullable=False)
    duration_above_ic90_hours = Column(Float, default=18.5, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    simulation = relationship("DBPkPdSimulation", back_populates="pd_effects")
