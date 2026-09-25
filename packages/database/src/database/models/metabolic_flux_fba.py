"""Genome-Scale Metabolic Network Flux Balance Analysis (FBA) Model."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


class DBMetabolicFluxFBASStudy(Base):
    """Database model for genome-scale metabolic flux balance analysis (FBA)."""

    __tablename__ = "metabolic_flux_fba_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_name = Column(String(255), nullable=False, index=True)
    organism_model = Column(String(64), nullable=False, default="Human Recon3D")
    cellular_phenotype = Column(String(64), nullable=False, default="Warburg Glycolytic Cancer")
    optimal_growth_rate_hr = Column(Float, nullable=False, default=0.084)
    objective_reaction = Column(String(64), nullable=False, default="Biomass_Eukaryote_Production")
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

    reactions = relationship(
        "DBReactionFluxConstraint",
        back_populates="study",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    vulnerabilities = relationship(
        "DBMetabolicVulnerabilityHit",
        back_populates="study",
        cascade="all, delete-orphan",
        lazy="joined",
    )


class DBReactionFluxConstraint(Base):
    """Database model for metabolic reaction flux boundaries and LP solution rates."""

    __tablename__ = "reaction_flux_constraints"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("metabolic_flux_fba_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    reaction_id = Column(String(64), nullable=False)
    reaction_name = Column(String(128), nullable=False)
    subsystem = Column(String(64), nullable=False)
    lower_bound = Column(Float, nullable=False)
    upper_bound = Column(Float, nullable=False)
    computed_flux_mmol_gdw_hr = Column(Float, nullable=False)
    shadow_price = Column(Float, nullable=False, default=0.0)
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    study = relationship("DBMetabolicFluxFBASStudy", back_populates="reactions")


class DBMetabolicVulnerabilityHit(Base):
    """Database model for single/double reaction knockout vulnerability targets."""

    __tablename__ = "metabolic_vulnerability_hits"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("metabolic_flux_fba_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    target_enzyme_gene = Column(String(64), nullable=False)
    target_reaction = Column(String(64), nullable=False)
    growth_inhibition_percent = Column(Float, nullable=False)
    synthetic_lethal_partner = Column(String(64), nullable=True)
    druggability_verdict = Column(String(32), nullable=False, default="druggable_selective")
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    study = relationship("DBMetabolicFluxFBASStudy", back_populates="vulnerabilities")
