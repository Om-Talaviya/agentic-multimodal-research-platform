"""
Repository for Phase 139: Spatial Multi-Omics Cell-Cell GNN Neighborhood Co-Occurrence Matrix Engine.
"""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from database.models.spatial_gnn_neighborhood import (
    DBSpatialGNNNeighborhood,
    DBCellTypeProximityGraph,
    DBSpatialMicrodomainNiche,
)


class SpatialGNNNeighborhoodRepository:
    """Repository handling CRUD operations for spatial multi-omics GNN graphs, proximity matrices, and microdomain niches."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_neighborhood(
        self,
        dataset_name: str,
        tissue_type: str,
        total_single_cells_indexed: int = 45000,
        graph_connectivity_radius_um: float = 50.0,
        gnn_embedding_dimension: int = 128,
        spatial_homophily_ratio: float = 0.68,
        metadata_json: Optional[Dict[str, Any]] = None,
        project_id: Optional[uuid.UUID] = None,
    ) -> DBSpatialGNNNeighborhood:
        """Create a new spatial GNN neighborhood record."""
        neighborhood = DBSpatialGNNNeighborhood(
            id=uuid.uuid4(),
            project_id=project_id,
            dataset_name=dataset_name,
            tissue_type=tissue_type,
            total_single_cells_indexed=total_single_cells_indexed,
            graph_connectivity_radius_um=graph_connectivity_radius_um,
            gnn_embedding_dimension=gnn_embedding_dimension,
            spatial_homophily_ratio=spatial_homophily_ratio,
            metadata_json=metadata_json or {},
        )
        self.session.add(neighborhood)
        await self.session.commit()
        await self.session.refresh(neighborhood)
        return neighborhood

    async def get_neighborhood(self, neighborhood_id: uuid.UUID) -> Optional[DBSpatialGNNNeighborhood]:
        """Get spatial neighborhood with proximity graphs and microdomain niches."""
        stmt = (
            select(DBSpatialGNNNeighborhood)
            .options(
                selectinload(DBSpatialGNNNeighborhood.proximity_graphs),
                selectinload(DBSpatialGNNNeighborhood.microdomain_niches),
            )
            .where(DBSpatialGNNNeighborhood.id == neighborhood_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_neighborhoods(self, limit: int = 50, offset: int = 0) -> List[DBSpatialGNNNeighborhood]:
        """List all spatial GNN neighborhoods."""
        stmt = (
            select(DBSpatialGNNNeighborhood)
            .order_by(desc(DBSpatialGNNNeighborhood.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_proximity_graph(
        self,
        neighborhood_id: uuid.UUID,
        source_cell_type: str,
        target_cell_type: str,
        interaction_frequency: int,
        spatial_enrichment_z_score: float,
        ligand_receptor_potential_score: float,
    ) -> DBCellTypeProximityGraph:
        """Add a cell-cell proximity interaction edge."""
        edge = DBCellTypeProximityGraph(
            id=uuid.uuid4(),
            neighborhood_id=neighborhood_id,
            source_cell_type=source_cell_type,
            target_cell_type=target_cell_type,
            interaction_frequency=interaction_frequency,
            spatial_enrichment_z_score=spatial_enrichment_z_score,
            ligand_receptor_potential_score=ligand_receptor_potential_score,
        )
        self.session.add(edge)
        await self.session.commit()
        await self.session.refresh(edge)
        return edge

    async def add_microdomain_niche(
        self,
        neighborhood_id: uuid.UUID,
        niche_cluster_id: str,
        dominant_cell_composition: str,
        mean_distance_to_vasculature_um: float,
        hypoxia_signature_enrichment: float,
    ) -> DBSpatialMicrodomainNiche:
        """Add an identified spatial microdomain niche."""
        niche = DBSpatialMicrodomainNiche(
            id=uuid.uuid4(),
            neighborhood_id=neighborhood_id,
            niche_cluster_id=niche_cluster_id,
            dominant_cell_composition=dominant_cell_composition,
            mean_distance_to_vasculature_um=mean_distance_to_vasculature_um,
            hypoxia_signature_enrichment=hypoxia_signature_enrichment,
        )
        self.session.add(niche)
        await self.session.commit()
        await self.session.refresh(niche)
        return niche
