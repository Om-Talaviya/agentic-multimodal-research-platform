"""Repository for Multiplexed Spatial Proteomics & IMC data access (Phase 102)."""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.models.spatial_proteomics import (
    DBSpatialProteomicsExperiment,
    DBChannelMarkerIntensity,
    DBCellularNeighborhoodSpatialMatrix,
)


class SpatialProteomicsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_experiment(
        self,
        workspace_id: uuid.UUID,
        sample_name: str,
        tissue_origin: str,
        imaging_modality: str = "Hyperion Imaging Mass Cytometry",
        total_channels: int = 40,
        total_segmented_cells: int = 24500,
        mean_cellular_density_per_mm2: float = 3200.0,
        immune_infiltration_score: float = 78.5,
        tumor_stroma_mixing_entropy: float = 0.812,
        analysis_metadata: Optional[Dict[str, Any]] = None,
    ) -> DBSpatialProteomicsExperiment:
        exp = DBSpatialProteomicsExperiment(
            workspace_id=workspace_id,
            sample_name=sample_name,
            tissue_origin=tissue_origin,
            imaging_modality=imaging_modality,
            total_channels=total_channels,
            total_segmented_cells=total_segmented_cells,
            mean_cellular_density_per_mm2=mean_cellular_density_per_mm2,
            immune_infiltration_score=immune_infiltration_score,
            tumor_stroma_mixing_entropy=tumor_stroma_mixing_entropy,
            analysis_metadata=analysis_metadata or {},
        )
        self.session.add(exp)
        await self.session.commit()
        await self.session.refresh(exp)
        return exp

    async def add_marker_channel(
        self,
        experiment_id: uuid.UUID,
        metal_isotope_tag: str,
        antibody_target: str,
        mean_signal_intensity: float,
        signal_to_noise_ratio: float = 14.2,
        positive_cells_percentage: float = 24.5,
    ) -> DBChannelMarkerIntensity:
        ch = DBChannelMarkerIntensity(
            experiment_id=experiment_id,
            metal_isotope_tag=metal_isotope_tag,
            antibody_target=antibody_target,
            mean_signal_intensity=mean_signal_intensity,
            signal_to_noise_ratio=signal_to_noise_ratio,
            positive_cells_percentage=positive_cells_percentage,
        )
        self.session.add(ch)
        await self.session.commit()
        await self.session.refresh(ch)
        return ch

    async def add_neighborhood(
        self,
        experiment_id: uuid.UUID,
        neighborhood_cluster_name: str,
        dominant_cell_type: str,
        neighbor_cell_count: int,
        interaction_enrichment_z_score: float = 3.45,
    ) -> DBCellularNeighborhoodSpatialMatrix:
        nh = DBCellularNeighborhoodSpatialMatrix(
            experiment_id=experiment_id,
            neighborhood_cluster_name=neighborhood_cluster_name,
            dominant_cell_type=dominant_cell_type,
            neighbor_cell_count=neighbor_cell_count,
            interaction_enrichment_z_score=interaction_enrichment_z_score,
        )
        self.session.add(nh)
        await self.session.commit()
        await self.session.refresh(nh)
        return nh

    async def get_experiment(self, experiment_id: uuid.UUID) -> Optional[DBSpatialProteomicsExperiment]:
        stmt = (
            select(DBSpatialProteomicsExperiment)
            .options(
                selectinload(DBSpatialProteomicsExperiment.marker_channels),
                selectinload(DBSpatialProteomicsExperiment.neighborhoods),
            )
            .where(DBSpatialProteomicsExperiment.id == experiment_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
