"""
Phase 109: High-Dimensional CyTOF & Mass Cytometry Phenotyper Models.
"""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID, JSON

class DBCyTOFExperiment(Base):
    __tablename__ = "cytof_experiments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(String(100), nullable=True)
    experiment_name = Column(String(200), nullable=False)
    tissue_type = Column(String(100), nullable=False, default="PBMC")
    cell_count = Column(Integer, nullable=False, default=5000)
    panel_size = Column(Integer, nullable=False, default=35)
    cofactor = Column(Float, nullable=False, default=5.0)
    is_compensated = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    channels = relationship("DBCyTOFMetalChannel", back_populates="experiment", cascade="all, delete-orphan")
    clusters = relationship("DBSingleCellCyTOFCluster", back_populates="experiment", cascade="all, delete-orphan")


class DBCyTOFMetalChannel(Base):
    __tablename__ = "cytof_metal_channels"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(GUID(), ForeignKey("cytof_experiments.id", ondelete="CASCADE"), nullable=False)
    channel_name = Column(String(100), nullable=False)  # e.g. "141Pr_CD3"
    metal_isotope = Column(String(50), nullable=False)   # e.g. "141Pr"
    target_marker = Column(String(100), nullable=False)  # e.g. "CD3"
    spillover_matrix = Column(JSON, nullable=True)       # Cross-channel spillover coefficients
    mean_intensity = Column(Float, nullable=False, default=0.0)
    signal_to_noise = Column(Float, nullable=False, default=10.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    experiment = relationship("DBCyTOFExperiment", back_populates="channels")


class DBSingleCellCyTOFCluster(Base):
    __tablename__ = "cytof_single_cell_clusters"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(GUID(), ForeignKey("cytof_experiments.id", ondelete="CASCADE"), nullable=False)
    cluster_id = Column(Integer, nullable=False)
    cluster_name = Column(String(150), nullable=False)
    cell_frequency = Column(Float, nullable=False)       # Percentage of total cells
    marker_enrichment_profile = Column(JSON, nullable=False) # {marker: expression_z_score}
    phenograph_k = Column(Integer, nullable=False, default=30)
    tsne_coordinates_2d = Column(JSON, nullable=True)   # Sample coordinates for visualization
    created_at = Column(DateTime, default=datetime.utcnow)

    experiment = relationship("DBCyTOFExperiment", back_populates="clusters")
