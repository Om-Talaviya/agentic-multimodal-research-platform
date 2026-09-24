"""Repository for Spatial RNA Velocity (Phase 146)."""

import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.models.spatial_rna_velocity import (
    DBSpatialRNAVelocityStudy,
    DBVelocityVectorFieldSpot,
    DBMorphogenesisStreamline,
)


class SpatialRNAVelocityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_study(
        self,
        tissue_sample_name: str,
        developmental_stage: str,
        spot_count: int,
        mean_velocity_magnitude: float,
        coherence_score: float,
    ) -> DBSpatialRNAVelocityStudy:
        study = DBSpatialRNAVelocityStudy(
            tissue_sample_name=tissue_sample_name,
            developmental_stage=developmental_stage,
            spot_count=spot_count,
            mean_velocity_magnitude=mean_velocity_magnitude,
            coherence_score=coherence_score,
        )
        self.db.add(study)
        await self.db.commit()
        await self.db.refresh(study)
        return study

    async def add_vector_spot(
        self,
        study_id: uuid.UUID,
        spot_index: int,
        x_coord_um: float,
        y_coord_um: float,
        vx_vector: float,
        vy_vector: float,
        cell_type_annotation: str,
    ) -> DBVelocityVectorFieldSpot:
        spot = DBVelocityVectorFieldSpot(
            study_id=study_id,
            spot_index=spot_index,
            x_coord_um=x_coord_um,
            y_coord_um=y_coord_um,
            vx_vector=vx_vector,
            vy_vector=vy_vector,
            cell_type_annotation=cell_type_annotation,
        )
        self.db.add(spot)
        await self.db.commit()
        await self.db.refresh(spot)
        return spot

    async def add_streamline(
        self,
        study_id: uuid.UUID,
        streamline_id: str,
        origin_cell_state: str,
        terminal_cell_state: str,
        pseudotime_length: float,
    ) -> DBMorphogenesisStreamline:
        sl = DBMorphogenesisStreamline(
            study_id=study_id,
            streamline_id=streamline_id,
            origin_cell_state=origin_cell_state,
            terminal_cell_state=terminal_cell_state,
            pseudotime_length=pseudotime_length,
        )
        self.db.add(sl)
        await self.db.commit()
        await self.db.refresh(sl)
        return sl

    async def get_study_with_details(self, study_id: uuid.UUID) -> Optional[DBSpatialRNAVelocityStudy]:
        stmt = (
            select(DBSpatialRNAVelocityStudy)
            .where(DBSpatialRNAVelocityStudy.id == study_id)
            .options(
                selectinload(DBSpatialRNAVelocityStudy.vector_spots),
                selectinload(DBSpatialRNAVelocityStudy.streamlines),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
