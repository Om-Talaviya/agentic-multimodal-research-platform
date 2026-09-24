"""Repository for Glycomics Microarray (Phase 148)."""

import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.glycan_microarray import (
    DBGlycanMicroarrayScreen,
    DBGlycanSpotBindingRecord,
    DBLectinSpecificityProfile,
)


class GlycanMicroarrayRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_screen(
        self,
        target_lectin_name: str,
        organism_source: str,
        array_spots_count: int,
        mean_signal_to_noise: float,
        primary_epitope_motif: str,
        kd_apparent_nM: float,
    ) -> DBGlycanMicroarrayScreen:
        screen = DBGlycanMicroarrayScreen(
            id=uuid.uuid4(),
            target_lectin_name=target_lectin_name,
            organism_source=organism_source,
            array_spots_count=array_spots_count,
            mean_signal_to_noise=mean_signal_to_noise,
            primary_epitope_motif=primary_epitope_motif,
            kd_apparent_nM=kd_apparent_nM,
        )
        self.db.add(screen)
        await self.db.commit()
        await self.db.refresh(screen)
        return screen

    async def add_spot_record(
        self,
        screen_id: uuid.UUID,
        glycan_iupac: str,
        spot_index: int,
        fluorescence_rfu: float,
        z_score: float,
        relative_affinity: float,
    ) -> DBGlycanSpotBindingRecord:
        rec = DBGlycanSpotBindingRecord(
            id=uuid.uuid4(),
            screen_id=screen_id,
            glycan_iupac=glycan_iupac,
            spot_index=spot_index,
            fluorescence_rfu=fluorescence_rfu,
            z_score=z_score,
            relative_affinity=relative_affinity,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def add_specificity_profile(
        self,
        screen_id: uuid.UUID,
        glycan_motif: str,
        enrichment_fold: float,
        p_value_log10: float,
        selectivity_index: float,
    ) -> DBLectinSpecificityProfile:
        rec = DBLectinSpecificityProfile(
            id=uuid.uuid4(),
            screen_id=screen_id,
            glycan_motif=glycan_motif,
            enrichment_fold=enrichment_fold,
            p_value_log10=p_value_log10,
            selectivity_index=selectivity_index,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def get_screen_with_details(self, screen_id: uuid.UUID) -> Optional[DBGlycanMicroarrayScreen]:
        stmt = (
            select(DBGlycanMicroarrayScreen)
            .where(DBGlycanMicroarrayScreen.id == screen_id)
            .options(
                selectinload(DBGlycanMicroarrayScreen.spot_records),
                selectinload(DBGlycanMicroarrayScreen.specificity_profiles),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
