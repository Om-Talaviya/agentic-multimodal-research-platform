"""
SQLAlchemy Models for Phase 165: Peptide-Drug Conjugate (PDC) Linker Cleavability & Cathepsin-B Selectivity Engine.
"""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey
from database.connection import Base
from database.models.memory import GUID
from sqlalchemy.orm import relationship


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBPDCConjugateStudy(Base):
    __tablename__ = "pdc_conjugate_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID(), nullable=True, index=True)
    pdc_name = Column(String(255), nullable=False)
    homing_peptide_sequence = Column(String(255), nullable=False)
    linker_type = Column(String(100), default="Val-Cit-PABC")
    cytotoxic_payload = Column(String(100), default="Monomethyl Auristatin E (MMAE)")
    plasma_stability_half_life_hours = Column(Float, nullable=False)
    tumor_cathepsin_cleavage_rate_kcat_km = Column(Float, nullable=False)
    therapeutic_index_ratio = Column(Float, nullable=False)
    bystander_payload_diffusion_score = Column(Float, default=0.75)
    created_at = Column(DateTime, default=utc_now)

    cleavage_profiles = relationship(
        "DBPeptideLinkerCleavageProfile",
        back_populates="study",
        cascade="all, delete-orphan",
    )
    cathepsin_assays = relationship(
        "DBCathepsinBSelectivityAssay",
        back_populates="study",
        cascade="all, delete-orphan",
    )


class DBPeptideLinkerCleavageProfile(Base):
    __tablename__ = "peptide_linker_cleavage_profiles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("pdc_conjugate_studies.id"), nullable=False, index=True)
    enzyme_target = Column(String(100), default="Cathepsin-B")
    cleavage_efficiency_percent = Column(Float, nullable=False)
    incubation_time_minutes = Column(Float, default=60.0)
    intact_conjugate_remaining_percent = Column(Float, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    study = relationship("DBPDCConjugateStudy", back_populates="cleavage_profiles")


class DBCathepsinBSelectivityAssay(Base):
    __tablename__ = "cathepsin_b_selectivity_assays"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("pdc_conjugate_studies.id"), nullable=False, index=True)
    tissue_compartment = Column(String(100), nullable=False)  # Tumor Stroma, Normal Liver, Systemic Plasma
    enzymatic_activity_units = Column(Float, nullable=False)
    payload_release_velocity_nmol_min = Column(Float, nullable=False)
    selectivity_fold_enrichment = Column(Float, default=1.0)
    created_at = Column(DateTime, default=utc_now)

    study = relationship("DBPDCConjugateStudy", back_populates="cathepsin_assays")
