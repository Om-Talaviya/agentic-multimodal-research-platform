"""Cytochrome P450 Drug Metabolism & Isoform Inhibition Models (Phase 142)."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import JSON, GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBCYP450MetabolismScreen(Base):
    """CYP450 substrate and inhibition profile screen."""

    __tablename__ = "cyp450_metabolism_screens"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    compound_name = Column(String(255), nullable=False)
    smiles = Column(String(1000), nullable=False)
    intrinsic_clearance_ml_min_kg = Column(Float, default=0.0)
    hepatic_extraction_ratio = Column(Float, default=0.0)
    primary_metabolic_site = Column(String(100), default="Aromatic Hydroxylation")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    isoform_profiles = relationship("DBCYPIsoformProfile", back_populates="screen", cascade="all, delete-orphan")
    clearance_records = relationship("DBMetabolicClearanceRecord", back_populates="screen", cascade="all, delete-orphan")


class DBCYPIsoformProfile(Base):
    """Major CYP isoform inhibition and substrate affinity (3A4, 2D6, 2C9, 2C19, 1A2)."""

    __tablename__ = "cyp_isoform_profiles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    screen_id = Column(GUID(), ForeignKey("cyp450_metabolism_screens.id", ondelete="CASCADE"), nullable=False)
    isoform_name = Column(String(50), nullable=False)
    inhibition_ic50_um = Column(Float, nullable=False)
    is_inhibitor = Column(Boolean, default=False)
    is_substrate = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    screen = relationship("DBCYP450MetabolismScreen", back_populates="isoform_profiles")


class DBMetabolicClearanceRecord(Base):
    """Human liver microsome (HLM) kinetic clearance timepoint."""

    __tablename__ = "metabolic_clearance_records"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    screen_id = Column(GUID(), ForeignKey("cyp450_metabolism_screens.id", ondelete="CASCADE"), nullable=False)
    incubation_time_min = Column(Integer, nullable=False)
    parent_remaining_percent = Column(Float, nullable=False)
    metabolite_formation_area = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    screen = relationship("DBCYP450MetabolismScreen", back_populates="clearance_records")
