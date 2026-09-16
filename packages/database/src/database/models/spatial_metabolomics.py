"""
SQLAlchemy models for Spatial Metabolomics & MALDI Imaging MS Flux Balance (Phase 57).
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


class DBSpatialMetabolomicsExperiment(Base):
    """Represents a MALDI mass spectrometry imaging experiment on tissue sections."""
    __tablename__ = "spatial_metabolomics_experiments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tissue_sample_id = Column(String(64), nullable=False)
    organ_type = Column(String(128), nullable=False)  # e.g. Brain, Liver, Tumor Microenvironment
    matrix_compound = Column(String(32), default="DHB")  # DHB, DAN, CHCA, NEDC
    spatial_resolution_um = Column(Float, default=20.0)  # 5um - 50um
    total_metabolites_identified = Column(Integer, default=0)
    status = Column(String(32), default="COMPLETED")
    metadata_info = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    metabolites = relationship("DBMetaboliteSpatialProfile", back_populates="experiment", cascade="all, delete-orphan")
    flux_routes = relationship("DBMetabolicFluxRoute", back_populates="experiment", cascade="all, delete-orphan")


class DBMetaboliteSpatialProfile(Base):
    """Represents a spatial distribution profile of an individual metabolite m/z."""
    __tablename__ = "spatial_metabolite_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_id = Column(String(36), ForeignKey("spatial_metabolomics_experiments.id", ondelete="CASCADE"), nullable=False)
    metabolite_name = Column(String(128), nullable=False)  # e.g. L-Lactate, Glutathione, ATP, PC(34:1)
    kegg_id = Column(String(16), nullable=True)  # e.g. C00186
    mz_ratio = Column(Float, nullable=False)
    spatial_zone = Column(String(64), default="Tumor Core")  # Tumor Core, Invasive Margin, Normal Stroma
    mean_intensity_au = Column(Float, nullable=False)
    fold_change_vs_normal = Column(Float, default=1.0)
    spatial_heterogeneity_score = Column(Float, default=0.75)
    created_at = Column(DateTime, default=datetime.utcnow)

    experiment = relationship("DBSpatialMetabolomicsExperiment", back_populates="metabolites")


class DBMetabolicFluxRoute(Base):
    """Represents a biological pathway flux estimation from spatial metabolomics constraints."""
    __tablename__ = "spatial_metabolic_flux_routes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_id = Column(String(36), ForeignKey("spatial_metabolomics_experiments.id", ondelete="CASCADE"), nullable=False)
    pathway_name = Column(String(128), nullable=False)  # Glycolysis, Warburg Effect, Glutaminolysis, Lipid Synthesis
    estimated_flux_rate = Column(Float, nullable=False)  # mmol/gDW/h
    pathway_activity_score = Column(Float, default=0.85)  # 0.0 - 1.0
    limiting_enzyme = Column(String(64), default="LDHA")
    created_at = Column(DateTime, default=datetime.utcnow)

    experiment = relationship("DBSpatialMetabolomicsExperiment", back_populates="flux_routes")
