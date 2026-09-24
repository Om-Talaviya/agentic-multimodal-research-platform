"""Phase 157: Cell-Free Protein Synthesis (CFPS) TX-TL Kinetics Models."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBCFPSTXTLKineticsStudy(Base):
    """Cell-free transcription-translation reaction modeling study."""

    __tablename__ = "cfps_txtl_kinetics_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    target_protein_name = Column(String(255), nullable=False)
    extract_system_type = Column(String(120), default="E. coli BL21 Star (DE3) Lysate")
    reaction_mode = Column(String(64), default="Continuous Exchange Cell-Free (CECF)")
    reaction_time_hours = Column(Float, default=12.0)
    final_protein_yield_mg_ml = Column(Float, default=0.0)
    transcription_rate_nt_s = Column(Float, default=0.0)
    translation_rate_aa_s = Column(Float, default=0.0)
    energy_regeneration_efficiency = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    yield_curves = relationship("DBRibosomeTranslationalYieldCurve", back_populates="study", cascade="all, delete-orphan")
    substrates = relationship("DBMetabolicSubstrateDepletionRecord", back_populates="study", cascade="all, delete-orphan")


class DBRibosomeTranslationalYieldCurve(Base):
    """Temporal protein accumulation trajectory during cell-free incubation."""

    __tablename__ = "ribosome_translational_yield_curves"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("cfps_txtl_kinetics_studies.id", ondelete="CASCADE"), nullable=False)
    time_elapsed_hours = Column(Float, nullable=False)
    mrna_concentration_uM = Column(Float, nullable=False)
    protein_concentration_mg_ml = Column(Float, nullable=False)
    ribosome_active_fraction = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBCFPSTXTLKineticsStudy", back_populates="yield_curves")


class DBMetabolicSubstrateDepletionRecord(Base):
    """Energy substrate and cofactor depletion record."""

    __tablename__ = "metabolic_substrate_depletion_records"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("cfps_txtl_kinetics_studies.id", ondelete="CASCADE"), nullable=False)
    substrate_name = Column(String(64), nullable=False)
    initial_concentration_mM = Column(Float, nullable=False)
    final_concentration_mM = Column(Float, nullable=False)
    consumption_rate_mM_h = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBCFPSTXTLKineticsStudy", back_populates="substrates")
