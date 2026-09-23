"""
Phase 139: Spatial Multi-Omics Cell-Cell GNN Neighborhood Co-Occurrence Matrix Database Models.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID, JSON


class DBSpatialGNNNeighborhood(Base):
    __tablename__ = "spatial_gnn_neighborhoods"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID, nullable=True, index=True)
    dataset_name = Column(String(255), nullable=False, index=True)
    tissue_type = Column(String(255), nullable=False)
    total_single_cells_indexed = Column(Integer, nullable=False, default=45000)
    graph_connectivity_radius_um = Column(Float, nullable=False, default=50.0)
    gnn_embedding_dimension = Column(Integer, nullable=False, default=128)
    spatial_homophily_ratio = Column(Float, nullable=False, default=0.68)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    proximity_graphs = relationship(
        "DBCellTypeProximityGraph",
        back_populates="neighborhood",
        cascade="all, delete-orphan",
    )
    microdomain_niches = relationship(
        "DBSpatialMicrodomainNiche",
        back_populates="neighborhood",
        cascade="all, delete-orphan",
    )


class DBCellTypeProximityGraph(Base):
    __tablename__ = "cell_type_proximity_graphs"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    neighborhood_id = Column(GUID, ForeignKey("spatial_gnn_neighborhoods.id", ondelete="CASCADE"), nullable=False, index=True)
    source_cell_type = Column(String(100), nullable=False)  # "CD8+ Cytotoxic T Cell"
    target_cell_type = Column(String(100), nullable=False)  # "Pancreatic Ductal Adenocarcinoma Cell"
    interaction_frequency = Column(Integer, nullable=False)
    spatial_enrichment_z_score = Column(Float, nullable=False)
    ligand_receptor_potential_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    neighborhood = relationship("DBSpatialGNNNeighborhood", back_populates="proximity_graphs")


class DBSpatialMicrodomainNiche(Base):
    __tablename__ = "spatial_microdomain_niches"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    neighborhood_id = Column(GUID, ForeignKey("spatial_gnn_neighborhoods.id", ondelete="CASCADE"), nullable=False, index=True)
    niche_cluster_id = Column(String(50), nullable=False)  # "Niche_01_Tertiary_Lymphoid_Structure"
    dominant_cell_composition = Column(String(255), nullable=False)
    mean_distance_to_vasculature_um = Column(Float, nullable=False)
    hypoxia_signature_enrichment = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    neighborhood = relationship("DBSpatialGNNNeighborhood", back_populates="microdomain_niches")
