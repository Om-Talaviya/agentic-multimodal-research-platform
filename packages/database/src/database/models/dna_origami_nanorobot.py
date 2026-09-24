"""Phase 149: 3D DNA Origami Nanorobot Design Models."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBDNAOrigamiDesignCampaign(Base):
    """3D DNA origami nanorobot design campaign."""

    __tablename__ = "dna_origami_design_campaigns"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    nanorobot_name = Column(String(255), nullable=False)
    geometry_type = Column(String(120), default="Hexagonal Barrel Capsule")
    scaffold_type = Column(String(120), default="M13mp18 Single-Stranded DNA")
    staple_strands_count = Column(Integer, default=0, nullable=False)
    predicted_melting_temp_c = Column(Float, default=0.0)
    folding_yield_percent = Column(Float, default=0.0)
    cargo_cavity_volume_nm3 = Column(Float, default=0.0)
    latch_trigger_affinity_nM = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    staples = relationship("DBStapleStrandCrossover", back_populates="campaign", cascade="all, delete-orphan")
    latches = relationship("DBAptamerLatchTrigger", back_populates="campaign", cascade="all, delete-orphan")


class DBStapleStrandCrossover(Base):
    """Individual staple strand crossover coordinate and sequence."""

    __tablename__ = "staple_strand_crossovers"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(GUID(), ForeignKey("dna_origami_design_campaigns.id", ondelete="CASCADE"), nullable=False)
    strand_index = Column(Integer, nullable=False)
    sequence_5to3 = Column(String(255), nullable=False)
    length_nt = Column(Integer, nullable=False)
    tm_celsius = Column(Float, nullable=False)
    crossover_count = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    campaign = relationship("DBDNAOrigamiDesignCampaign", back_populates="staples")


class DBAptamerLatchTrigger(Base):
    """Molecular latch mechanism for payload release."""

    __tablename__ = "aptamer_latch_triggers"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(GUID(), ForeignKey("dna_origami_design_campaigns.id", ondelete="CASCADE"), nullable=False)
    target_biomarker = Column(String(120), nullable=False)
    aptamer_sequence = Column(String(255), nullable=False)
    opening_half_life_min = Column(Float, nullable=False)
    selectivity_ratio = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    campaign = relationship("DBDNAOrigamiDesignCampaign", back_populates="latches")
