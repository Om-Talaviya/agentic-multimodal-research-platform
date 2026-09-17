"""Cryo-Electron Tomography (Cryo-ET) Subtomogram Averaging Models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base


class DBCryoETDataset(Base):
    """Cryo-ET Tomogram Reconstruction dataset metadata."""
    __tablename__ = "cryoet_datasets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sample_name = Column(String(255), nullable=False)
    specimen_organism = Column(String(128), nullable=False)
    cellular_compartment = Column(String(128), nullable=False, default="CYTOSOL")  # CYTOSOL, MEMBRANE, MITOCHONDRIA, NUCLEAR_PORE
    tilt_angle_min = Column(Float, nullable=False, default=-60.0)
    tilt_angle_max = Column(Float, nullable=False, default=60.0)
    total_tilt_images = Column(Integer, nullable=False, default=41)
    pixel_size_angstrom = Column(Float, nullable=False, default=1.35)
    nominal_defocus_um = Column(Float, nullable=False, default=-2.5)
    tomogram_dimensions_json = Column(JSON, default=lambda: {"x": 4096, "y": 4096, "z": 1024})
    dataset_metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    particles = relationship("DBSubtomogramParticle", back_populates="dataset", cascade="all, delete-orphan")
    refinements = relationship("DBAveragedStructureRefinement", back_populates="dataset", cascade="all, delete-orphan")


class DBSubtomogramParticle(Base):
    """Extracted 3D subtomogram particle with spatial coordinates and Euler orientation."""
    __tablename__ = "cryoet_subtomogram_particles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String(36), ForeignKey("cryoet_datasets.id", ondelete="CASCADE"), nullable=False)
    particle_index = Column(Integer, nullable=False)
    coord_x = Column(Float, nullable=False)
    coord_y = Column(Float, nullable=False)
    coord_z = Column(Float, nullable=False)
    euler_phi = Column(Float, nullable=False, default=0.0)
    euler_theta = Column(Float, nullable=False, default=0.0)
    euler_psi = Column(Float, nullable=False, default=0.0)
    cross_correlation_score = Column(Float, nullable=False, default=0.75)
    class_assignment = Column(String(32), nullable=False, default="CLASS_1")

    dataset = relationship("DBCryoETDataset", back_populates="particles")


class DBAveragedStructureRefinement(Base):
    """Consensus Subtomogram Average (STA) 3D density refinement."""
    __tablename__ = "cryoet_averaged_refinements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String(36), ForeignKey("cryoet_datasets.id", ondelete="CASCADE"), nullable=False)
    class_name = Column(String(64), nullable=False, default="Consensus Class 1")
    particles_averaged_count = Column(Integer, nullable=False, default=100)
    estimated_resolution_angstrom = Column(Float, nullable=False, default=4.2)
    fsc_0143_spatial_frequency = Column(Float, nullable=False, default=0.238)  # 1/Angstrom
    b_factor_sharpening = Column(Float, nullable=False, default=-120.0)
    fsc_curve_json = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("DBCryoETDataset", back_populates="refinements")
