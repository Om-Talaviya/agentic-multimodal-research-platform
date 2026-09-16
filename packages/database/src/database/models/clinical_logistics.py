"""
SQLAlchemy models for Global Multi-Site Clinical Trial Logistics (Phase 63).
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


class DBClinicalTrialNetwork(Base):
    """Represents a global multi-center clinical trial logistics network."""
    __tablename__ = "clinical_trial_networks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trial_protocol_number = Column(String(64), nullable=False)  # e.g., PROTO-IMM-2026-03
    trial_title = Column(String(255), nullable=False)
    phase = Column(String(32), default="Phase III")
    product_storage_regime = Column(String(64), default="Ultra-Cold Chain (-80°C)")
    total_sites = Column(Integer, default=0)
    global_supply_risk_index = Column(Float, default=0.25)  # 0.0 - 1.0 (lower is better)
    status = Column(String(32), default="ACTIVE")
    metadata_info = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    sites = relationship("DBClinicalSiteNode", back_populates="network", cascade="all, delete-orphan")
    routes = relationship("DBLogisticsSupplyRoute", back_populates="network", cascade="all, delete-orphan")


class DBClinicalSiteNode(Base):
    """Represents an individual clinical hospital / investigative trial site."""
    __tablename__ = "clinical_site_nodes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    network_id = Column(String(36), ForeignKey("clinical_trial_networks.id", ondelete="CASCADE"), nullable=False)
    site_name = Column(String(128), nullable=False)  # e.g. Johns Hopkins, Charité Berlin, Tokyo University
    country_code = Column(String(8), nullable=False)  # US, DE, JP, UK
    active_enrolled_patients = Column(Integer, default=15)
    current_inventory_vials = Column(Integer, default=60)
    inventory_runway_days = Column(Float, default=45.0)
    cold_chain_compliance_pct = Column(Float, default=99.2)
    stockout_risk_score = Column(Float, default=0.15)
    created_at = Column(DateTime, default=datetime.utcnow)

    network = relationship("DBClinicalTrialNetwork", back_populates="sites")


class DBLogisticsSupplyRoute(Base):
    """Represents a cold-chain shipping lane between central depot and trial site."""
    __tablename__ = "clinical_logistics_routes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    network_id = Column(String(36), ForeignKey("clinical_trial_networks.id", ondelete="CASCADE"), nullable=False)
    origin_depot = Column(String(128), nullable=False)  # Central Depot Brussels
    destination_site = Column(String(128), nullable=False)  # Charité Berlin
    transport_mode = Column(String(64), default="Cryo-Courier Air Express")
    transit_time_hours = Column(Float, default=18.0)
    temperature_excursion_risk_pct = Column(Float, default=1.8)
    customs_clearance_delay_risk_pct = Column(Float, default=3.5)
    contingency_action = Column(String(255), default="Automated rerouting to secondary depot")
    created_at = Column(DateTime, default=datetime.utcnow)

    network = relationship("DBClinicalTrialNetwork", back_populates="routes")
