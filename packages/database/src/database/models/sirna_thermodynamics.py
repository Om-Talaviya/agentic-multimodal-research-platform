"""siRNA Duplex Thermodynamics & Off-Target Seed Suppressor Model."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


class DBsiRNAThermodynamicsStudy(Base):
    """Database model for siRNA thermodynamics and off-target screening studies."""

    __tablename__ = "sirna_thermodynamics_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_name = Column(String(255), nullable=False, index=True)
    target_mrna_transcript = Column(String(128), nullable=False, default="NM_000546.6 (TP53)")
    target_gene = Column(String(64), nullable=False, default="TP53")
    candidates_screened = Column(Integer, nullable=False, default=4)
    best_candidate_guide_strand = Column(String(128), nullable=False)
    mean_on_target_efficiency = Column(Float, nullable=False, default=88.5)
    summary_metrics = Column(JSON, nullable=True)
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )
    updated_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    duplexes = relationship(
        "DBsiRNADuplexConstruct",
        back_populates="study",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    off_targets = relationship(
        "DBOffTargetSeedMatch",
        back_populates="study",
        cascade="all, delete-orphan",
        lazy="joined",
    )


class DBsiRNADuplexConstruct(Base):
    """Database model for individual siRNA duplex thermodynamic candidates."""

    __tablename__ = "sirna_duplex_constructs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("sirna_thermodynamics_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    guide_strand_sequence = Column(String(64), nullable=False)
    passenger_strand_sequence = Column(String(64), nullable=False)
    delta_g_5p_kcal_mol = Column(Float, nullable=False)
    delta_g_3p_kcal_mol = Column(Float, nullable=False)
    delta_delta_g_asymmetry = Column(Float, nullable=False)
    seed_region_tm_celsius = Column(Float, nullable=False)
    risc_loading_preference = Column(String(32), nullable=False, default="guide_dominant")
    predicted_knockdown_efficiency = Column(Float, nullable=False)
    chemical_mod_pattern = Column(String(128), nullable=False, default="2OMe_2F_phosphorothioate")
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    study = relationship("DBsiRNAThermodynamicsStudy", back_populates="duplexes")


class DBOffTargetSeedMatch(Base):
    """Database model for off-target 3' UTR hexamer/heptamer seed matches."""

    __tablename__ = "sirna_off_target_seed_matches"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("sirna_thermodynamics_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    off_target_gene = Column(String(64), nullable=False)
    utr3_seed_match_type = Column(String(32), nullable=False, default="7mer-m8")
    seed_binding_free_energy = Column(Float, nullable=False)
    off_target_silencing_risk = Column(String(32), nullable=False, default="low")
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    study = relationship("DBsiRNAThermodynamicsStudy", back_populates="off_targets")
