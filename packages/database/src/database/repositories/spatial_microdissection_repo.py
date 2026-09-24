"""
Repository for Phase 162: Spatial Microdissection & Subcellular Spot Deconvolution.
"""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.spatial_microdissection import (
    DBSpatialMicrodissectionSession,
    DBSubcellularSpotDeconvolution,
    DBCellularNicheBoundary,
)


class SpatialMicrodissectionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self,
        sample_name: str,
        tissue_type: str,
        total_spots_analyzed: int = 0,
        subcellular_resolution_nm: float = 100.0,
        deconvolution_algorithm: str = "Subcellular-NMF-Bayesian",
        mean_cell_type_entropy: float = 0.0,
        project_id: Optional[uuid.UUID] = None,
    ) -> DBSpatialMicrodissectionSession:
        session = DBSpatialMicrodissectionSession(
            sample_name=sample_name,
            tissue_type=tissue_type,
            total_spots_analyzed=total_spots_analyzed,
            subcellular_resolution_nm=subcellular_resolution_nm,
            deconvolution_algorithm=deconvolution_algorithm,
            mean_cell_type_entropy=mean_cell_type_entropy,
            project_id=project_id,
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def add_spot_deconvolution(
        self,
        session_id: uuid.UUID,
        spot_index: int,
        spatial_x_coord: float,
        spatial_y_coord: float,
        dominant_cell_type: str,
        dominant_cell_proportion: float,
        cell_type_composition: Dict[str, float],
        rna_transcripts_count: int = 0,
    ) -> DBSubcellularSpotDeconvolution:
        spot = DBSubcellularSpotDeconvolution(
            session_id=session_id,
            spot_index=spot_index,
            spatial_x_coord=spatial_x_coord,
            spatial_y_coord=spatial_y_coord,
            dominant_cell_type=dominant_cell_type,
            dominant_cell_proportion=dominant_cell_proportion,
            cell_type_composition_json=cell_type_composition,
            rna_transcripts_count=rna_transcripts_count,
        )
        self.db.add(spot)
        await self.db.commit()
        await self.db.refresh(spot)
        return spot

    async def add_niche_boundary(
        self,
        session_id: uuid.UUID,
        niche_name: str,
        boundary_polygon: List[Dict[str, float]],
        niche_cellularity_score: float = 0.0,
        tumor_immune_interface_distance_um: float = 0.0,
    ) -> DBCellularNicheBoundary:
        boundary = DBCellularNicheBoundary(
            session_id=session_id,
            niche_name=niche_name,
            boundary_polygon_json=boundary_polygon,
            niche_cellularity_score=niche_cellularity_score,
            tumor_immune_interface_distance_um=tumor_immune_interface_distance_um,
        )
        self.db.add(boundary)
        await self.db.commit()
        await self.db.refresh(boundary)
        return boundary

    async def get_session(self, session_id: uuid.UUID) -> Optional[DBSpatialMicrodissectionSession]:
        stmt = (
            select(DBSpatialMicrodissectionSession)
            .options(
                selectinload(DBSpatialMicrodissectionSession.deconvolutions),
                selectinload(DBSpatialMicrodissectionSession.niche_boundaries),
            )
            .where(DBSpatialMicrodissectionSession.id == session_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()
