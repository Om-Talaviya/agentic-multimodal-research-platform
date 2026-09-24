"""Phase 150: Single-Cell Spatial Flux Balance Analysis Models."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBSingleCellSpatialFluxStudy(Base):
    """Single-cell spatial flux balance and microenvironment metabolic study."""

    __tablename__ = "single_cell_spatial_flux_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    tissue_sample_id = Column(String(255), nullable=False)
    organ_context = Column(String(120), default="Tumor Microenvironment")
    single_cells_simulated = Column(Integer, default=0, nullable=False)
    mean_glycolytic_flux = Column(Float, default=0.0)
    mean_oxphos_flux = Column(Float, default=0.0)
    lactate_secretion_rate = Column(Float, default=0.0)
    atp_generation_rate = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    flux_rates = relationship("DBMetabolicReactionFluxRate", back_populates="study", cascade="all, delete-orphan")
    microdomains = relationship("DBTissueMicrodomainProfile", back_populates="study", cascade="all, delete-orphan")


class DBMetabolicReactionFluxRate(Base):
    """Specific pathway reaction flux rate mmol/gDW/h."""

    __tablename__ = "metabolic_reaction_flux_rates"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("single_cell_spatial_flux_studies.id", ondelete="CASCADE"), nullable=False)
    reaction_id = Column(String(120), nullable=False)
    reaction_name = Column(String(255), nullable=False)
    subsystem = Column(String(120), nullable=False)
    flux_rate_mmol_gdw_h = Column(Float, nullable=False)
    shadow_price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBSingleCellSpatialFluxStudy", back_populates="flux_rates")


class DBTissueMicrodomainProfile(Base):
    """Spatial microdomain coordinates and substrate availability."""

    __tablename__ = "tissue_microdomain_profiles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("single_cell_spatial_flux_studies.id", ondelete="CASCADE"), nullable=False)
    domain_name = Column(String(120), nullable=False)
    radial_distance_um = Column(Float, nullable=False)
    oxygen_concentration_uM = Column(Float, nullable=False)
    glucose_concentration_mM = Column(Float, nullable=False)
    warburg_phenotype_score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBSingleCellSpatialFluxStudy", back_populates="microdomains")
