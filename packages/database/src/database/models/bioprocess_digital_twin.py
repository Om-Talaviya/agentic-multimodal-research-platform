"""
SQLAlchemy models for Bioprocess Bioreactor Digital Twin & Optimizer (Phase 62).
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


class DBBioreactorRun(Base):
    """Represents a bioprocess fermentation run with digital twin telemetry."""
    __tablename__ = "bioreactor_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_name = Column(String(128), nullable=False)
    cell_line = Column(String(64), default="CHO-K1 (mAb Producer)")
    bioreactor_type = Column(String(64), default="Fed-Batch Stirred Tank")
    working_volume_liters = Column(Float, default=50.0)
    final_titer_g_l = Column(Float, default=4.8)
    final_viability_pct = Column(Float, default=92.5)
    status = Column(String(32), default="COMPLETED")
    metadata_info = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    telemetry_points = relationship("DBBioprocessTimeSeriesPoint", back_populates="run", cascade="all, delete-orphan")
    control_actions = relationship("DBBioprocessControlAction", back_populates="run", cascade="all, delete-orphan")


class DBBioprocessTimeSeriesPoint(Base):
    """Represents real-time sensory telemetry throughout the fermentation cycle."""
    __tablename__ = "bioprocess_telemetry"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String(36), ForeignKey("bioreactor_runs.id", ondelete="CASCADE"), nullable=False)
    time_hours = Column(Float, nullable=False)
    viable_cell_density_10e6_ml = Column(Float, nullable=False)
    cell_viability_pct = Column(Float, nullable=False)
    glucose_concentration_g_l = Column(Float, nullable=False)
    lactate_concentration_g_l = Column(Float, nullable=False)
    dissolved_oxygen_pct = Column(Float, default=40.0)
    ph_level = Column(Float, default=7.10)
    product_titer_g_l = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("DBBioreactorRun", back_populates="telemetry_points")


class DBBioprocessControlAction(Base):
    """Represents an autonomous control action recommended by digital twin MPC policy."""
    __tablename__ = "bioprocess_control_actions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String(36), ForeignKey("bioreactor_runs.id", ondelete="CASCADE"), nullable=False)
    time_hours = Column(Float, nullable=False)
    feed_rate_ml_h = Column(Float, nullable=False)
    agitation_rpm = Column(Float, default=180.0)
    sparge_o2_l_min = Column(Float, default=0.5)
    temperature_c = Column(Float, default=36.8)
    policy_action_name = Column(String(64), default="Glucose Bolus Feed")
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("DBBioreactorRun", back_populates="control_actions")
