"""Repository for Organoid Morphometry (Phase 147)."""

import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.organoid_morphometry import (
    DBOrganoidMorphometryStudy,
    DBOrganoidZStackProfile,
    DBOrganoidDrugDoseResponse,
)


class OrganoidMorphometryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_study(
        self,
        study_name: str,
        tumor_type: str,
        organoid_count: int,
        mean_diameter_um: float,
        mean_volume_um3: float,
        sphericity_index: float,
        necrotic_core_ratio: float,
        hypoxia_gradient_slope: float,
    ) -> DBOrganoidMorphometryStudy:
        study = DBOrganoidMorphometryStudy(
            id=uuid.uuid4(),
            study_name=study_name,
            tumor_type=tumor_type,
            organoid_count=organoid_count,
            mean_diameter_um=mean_diameter_um,
            mean_volume_um3=mean_volume_um3,
            sphericity_index=sphericity_index,
            necrotic_core_ratio=necrotic_core_ratio,
            hypoxia_gradient_slope=hypoxia_gradient_slope,
        )
        self.db.add(study)
        await self.db.commit()
        await self.db.refresh(study)
        return study

    async def add_z_stack(
        self,
        study_id: uuid.UUID,
        slice_depth_um: float,
        cross_sectional_area_um2: float,
        circularity: float,
        fluorescence_intensity: float,
        live_dead_ratio: float,
    ) -> DBOrganoidZStackProfile:
        rec = DBOrganoidZStackProfile(
            id=uuid.uuid4(),
            study_id=study_id,
            slice_depth_um=slice_depth_um,
            cross_sectional_area_um2=cross_sectional_area_um2,
            circularity=circularity,
            fluorescence_intensity=fluorescence_intensity,
            live_dead_ratio=live_dead_ratio,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def add_dose_response(
        self,
        study_id: uuid.UUID,
        compound_name: str,
        dose_uM: float,
        viability_pct: float,
        invasion_inhibition_pct: float,
        computed_ic50_uM: float,
    ) -> DBOrganoidDrugDoseResponse:
        rec = DBOrganoidDrugDoseResponse(
            id=uuid.uuid4(),
            study_id=study_id,
            compound_name=compound_name,
            dose_uM=dose_uM,
            viability_pct=viability_pct,
            invasion_inhibition_pct=invasion_inhibition_pct,
            computed_ic50_uM=computed_ic50_uM,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def get_study_with_details(self, study_id: uuid.UUID) -> Optional[DBOrganoidMorphometryStudy]:
        stmt = (
            select(DBOrganoidMorphometryStudy)
            .where(DBOrganoidMorphometryStudy.id == study_id)
            .options(
                selectinload(DBOrganoidMorphometryStudy.z_stacks),
                selectinload(DBOrganoidMorphometryStudy.dose_responses),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
