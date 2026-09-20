"""
SQLAlchemy database models for Phase 106: Spatial Lipidomics & Multi-Isotope Imaging Mass Spectrometry.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID

class DBSpatialLipidomicsDataset(Base):
    __tablename__ = "spatial_lipidomics_datasets"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=True, index=True)
    sample_name = Column(String(255), nullable=False, index=True)
    tissue_type = Column(String(100), default="Brain Sagittal Section", index=True)
    matrix_type = Column(String(50), default="DHB")
    laser_spatial_resolution_um = Column(Float, default=20.0)
    total_spots = Column(Integer, default=0)
    detected_lipid_classes = Column(Integer, default=0)
    metadata_json = Column(JSON, nullable=True)
    status = Column(String(50), default="COMPLETED")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lipid_species = relationship("DBLipidSpeciesIdentification", back_populates="dataset", cascade="all, delete-orphan")
    spatial_spots = relationship("DBSpatialIonIntensityMap", back_populates="dataset", cascade="all, delete-orphan")

class DBLipidSpeciesIdentification(Base):
    __tablename__ = "spatial_lipid_species"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(GUID(), ForeignKey("spatial_lipidomics_datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    mz_ratio = Column(Float, nullable=False, index=True)
    lipid_species = Column(String(100), nullable=False, index=True)
    lipid_class = Column(String(50), nullable=False, index=True)
    adduct_type = Column(String(20), default="[M+H]+")
    structural_formula = Column(String(100), nullable=True)
    mean_intensity = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("DBSpatialLipidomicsDataset", back_populates="lipid_species")
    spots = relationship("DBSpatialIonIntensityMap", back_populates="lipid_item", cascade="all, delete-orphan")

class DBSpatialIonIntensityMap(Base):
    __tablename__ = "spatial_ion_intensity_maps"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(GUID(), ForeignKey("spatial_lipidomics_datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    lipid_species_id = Column(GUID(), ForeignKey("spatial_lipid_species.id", ondelete="CASCADE"), nullable=False, index=True)
    x_coord = Column(Integer, nullable=False)
    y_coord = Column(Integer, nullable=False)
    normalized_intensity = Column(Float, default=0.0)
    region_annotation = Column(String(100), default="Cortex")
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("DBSpatialLipidomicsDataset", back_populates="spatial_spots")
    lipid_item = relationship("DBLipidSpeciesIdentification", back_populates="spots")
