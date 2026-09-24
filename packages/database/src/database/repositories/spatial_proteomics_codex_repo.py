"""Repository for Spatial Proteomics CODEX (Phase 155)."""

import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.spatial_proteomics_codex import (
    DBSpatialProteomicsCODEXStudy,
    DBCODEXProteinMarkerExpression,
    DBSingleCellSpatialNeighborhoodPhenotype,
)


class SpatialProteomicsCODEXRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_study(
        self,
        tissue_sample_name: str,
        organ_tissue_type: str,
        multiplex_panel_size: int,
        single_cells_segmented: int,
        cellular_neighborhoods_count: int,
        mean_signal_to_background: float,
        immune_infiltration_score: float,
    ) -> DBSpatialProteomicsCODEXStudy:
        study = DBSpatialProteomicsCODEXStudy(
            id=uuid.uuid4(),
            tissue_sample_name=tissue_sample_name,
            organ_tissue_type=organ_tissue_type,
            multiplex_panel_size=multiplex_panel_size,
            single_cells_segmented=single_cells_segmented,
            cellular_neighborhoods_count=cellular_neighborhoods_count,
            mean_signal_to_background=mean_signal_to_background,
            immune_infiltration_score=immune_infiltration_score,
        )
        self.db.add(study)
        await self.db.commit()
        await self.db.refresh(study)
        return study

    async def add_marker_expression(
        self,
        study_id: uuid.UUID,
        marker_name: str,
        cellular_compartment: str,
        mean_fluorescence_intensity: float,
        signal_to_noise_ratio: float,
        positive_cells_percentage: float,
    ) -> DBCODEXProteinMarkerExpression:
        rec = DBCODEXProteinMarkerExpression(
            id=uuid.uuid4(),
            study_id=study_id,
            marker_name=marker_name,
            cellular_compartment=cellular_compartment,
            mean_fluorescence_intensity=mean_fluorescence_intensity,
            signal_to_noise_ratio=signal_to_noise_ratio,
            positive_cells_percentage=positive_cells_percentage,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def add_neighborhood_phenotype(
        self,
        study_id: uuid.UUID,
        neighborhood_cluster_id: int,
        neighborhood_name: str,
        dominant_cell_type: str,
        radius_um: float,
        cell_density_per_mm2: float,
        immunosuppression_index: float,
    ) -> DBSingleCellSpatialNeighborhoodPhenotype:
        rec = DBSingleCellSpatialNeighborhoodPhenotype(
            id=uuid.uuid4(),
            study_id=study_id,
            neighborhood_cluster_id=neighborhood_cluster_id,
            neighborhood_name=neighborhood_name,
            dominant_cell_type=dominant_cell_type,
            radius_um=radius_um,
            cell_density_per_mm2=cell_density_per_mm2,
            immunosuppression_index=immunosuppression_index,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def get_study_with_details(self, study_id: uuid.UUID) -> Optional[DBSpatialProteomicsCODEXStudy]:
        stmt = (
            select(DBSpatialProteomicsCODEXStudy)
            .where(DBSpatialProteomicsCODEXStudy.id == study_id)
            .options(
                selectinload(DBSpatialProteomicsCODEXStudy.marker_expressions),
                selectinload(DBSpatialProteomicsCODEXStudy.neighborhood_phenotypes),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
