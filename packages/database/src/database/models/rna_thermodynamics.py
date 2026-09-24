"""
SQLAlchemy Models for Phase 163: Non-Coding RNA Secondary Structure Thermodynamics & Minimum Free Energy (MFE) Folding Engine.
"""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey
from database.connection import Base
from database.models.memory import GUID
from sqlalchemy.orm import relationship


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBRNAThermodynamicsStudy(Base):
    __tablename__ = "rna_thermodynamics_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID(), nullable=True, index=True)
    rna_name = Column(String(255), nullable=False)
    sequence = Column(String(4096), nullable=False)
    sequence_length = Column(Integer, default=0)
    dot_bracket_structure = Column(String(4096), nullable=False)
    mfe_delta_g_kcal_mol = Column(Float, nullable=False)
    ensemble_free_energy_kcal_mol = Column(Float, nullable=False)
    ensemble_defect_score = Column(Float, default=0.0)
    melting_temperature_tm_celsius = Column(Float, default=0.0)
    thermodynamic_ruleset = Column(String(100), default="Turner-2004-NearestNeighbor")
    created_at = Column(DateTime, default=utc_now)

    base_pairs = relationship(
        "DBRNABasePairProbability",
        back_populates="study",
        cascade="all, delete-orphan",
    )
    pseudoknots = relationship(
        "DBRNAPseudoknotStructure",
        back_populates="study",
        cascade="all, delete-orphan",
    )


class DBRNABasePairProbability(Base):
    __tablename__ = "rna_base_pair_probabilities"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("rna_thermodynamics_studies.id"), nullable=False, index=True)
    pos_i = Column(Integer, nullable=False)
    pos_j = Column(Integer, nullable=False)
    pairing_probability = Column(Float, nullable=False)
    base_pair_type = Column(String(10), default="Watson-Crick")
    created_at = Column(DateTime, default=utc_now)

    study = relationship("DBRNAThermodynamicsStudy", back_populates="base_pairs")


class DBRNAPseudoknotStructure(Base):
    __tablename__ = "rna_pseudoknot_structures"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("rna_thermodynamics_studies.id"), nullable=False, index=True)
    stem1_range = Column(String(50), nullable=False)
    stem2_range = Column(String(50), nullable=False)
    loop_topology = Column(String(100), default="H-type Pseudoknot")
    pseudoknot_stability_delta_g_kcal_mol = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utc_now)

    study = relationship("DBRNAThermodynamicsStudy", back_populates="pseudoknots")
