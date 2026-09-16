"""
SQLAlchemy models for Antibody-Drug Conjugate (ADC) Payload-Linker Design (Phase 59).
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


class DBADCDesignCampaign(Base):
    """Represents an ADC payload-linker optimization campaign."""
    __tablename__ = "adc_campaigns"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    antibody_name = Column(String(128), nullable=False)  # Trastuzumab, Sacituzumab, Datopotamab
    target_antigen = Column(String(64), nullable=False)  # HER2, TROP2, CEACAM5
    conjugation_chemistry = Column(String(64), default="Maleimide-Cysteine")
    target_dar = Column(Float, default=4.0)  # Drug-to-Antibody Ratio
    total_constructs_screened = Column(Integer, default=0)
    status = Column(String(32), default="COMPLETED")
    metadata_info = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    constructs = relationship("DBADCPayloadLinkerConstruct", back_populates="campaign", cascade="all, delete-orphan")


class DBADCPayloadLinkerConstruct(Base):
    """Represents an individual ADC candidate construct."""
    __tablename__ = "adc_constructs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String(36), ForeignKey("adc_campaigns.id", ondelete="CASCADE"), nullable=False)
    construct_code = Column(String(64), nullable=False)
    payload_name = Column(String(64), nullable=False)  # MMAE, DXd (Deruxtecan), DM1, PBD
    payload_class = Column(String(64), default="Topoisomerase I Inhibitor")
    linker_type = Column(String(64), default="Val-Cit (Cathepsin B Cleavable)")
    measured_dar = Column(Float, nullable=False)  # e.g., 3.8, 7.8
    bystander_killing_score = Column(Float, default=0.85)  # 0.0 - 1.0
    plasma_half_life_hours = Column(Float, default=168.0)  # 7 days
    aggregation_propensity_pct = Column(Float, default=1.8)
    therapeutic_index_score = Column(Float, nullable=False)
    recommended_lead = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("DBADCDesignCampaign", back_populates="constructs")
