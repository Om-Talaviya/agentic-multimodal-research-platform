"""Repository for CYP450 Metabolism (Phase 142)."""

import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.models.cyp450_metabolism import (
    DBCYP450MetabolismScreen,
    DBCYPIsoformProfile,
    DBMetabolicClearanceRecord,
)


class CYP450MetabolismRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_screen(
        self,
        compound_name: str,
        smiles: str,
        intrinsic_clearance_ml_min_kg: float,
        hepatic_extraction_ratio: float,
        primary_metabolic_site: str,
    ) -> DBCYP450MetabolismScreen:
        screen = DBCYP450MetabolismScreen(
            compound_name=compound_name,
            smiles=smiles,
            intrinsic_clearance_ml_min_kg=intrinsic_clearance_ml_min_kg,
            hepatic_extraction_ratio=hepatic_extraction_ratio,
            primary_metabolic_site=primary_metabolic_site,
        )
        self.db.add(screen)
        await self.db.commit()
        await self.db.refresh(screen)
        return screen

    async def add_isoform_profile(
        self,
        screen_id: uuid.UUID,
        isoform_name: str,
        inhibition_ic50_um: float,
        is_inhibitor: bool,
        is_substrate: bool,
    ) -> DBCYPIsoformProfile:
        prof = DBCYPIsoformProfile(
            screen_id=screen_id,
            isoform_name=isoform_name,
            inhibition_ic50_um=inhibition_ic50_um,
            is_inhibitor=is_inhibitor,
            is_substrate=is_substrate,
        )
        self.db.add(prof)
        await self.db.commit()
        await self.db.refresh(prof)
        return prof

    async def add_clearance_record(
        self,
        screen_id: uuid.UUID,
        incubation_time_min: int,
        parent_remaining_percent: float,
        metabolite_formation_area: float,
    ) -> DBMetabolicClearanceRecord:
        rec = DBMetabolicClearanceRecord(
            screen_id=screen_id,
            incubation_time_min=incubation_time_min,
            parent_remaining_percent=parent_remaining_percent,
            metabolite_formation_area=metabolite_formation_area,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def get_screen_with_details(self, screen_id: uuid.UUID) -> Optional[DBCYP450MetabolismScreen]:
        stmt = (
            select(DBCYP450MetabolismScreen)
            .where(DBCYP450MetabolismScreen.id == screen_id)
            .options(
                selectinload(DBCYP450MetabolismScreen.isoform_profiles),
                selectinload(DBCYP450MetabolismScreen.clearance_records),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
