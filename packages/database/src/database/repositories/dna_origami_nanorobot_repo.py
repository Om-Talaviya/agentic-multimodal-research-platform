"""Repository for DNA Origami Nanorobot (Phase 149)."""

import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.dna_origami_nanorobot import (
    DBDNAOrigamiDesignCampaign,
    DBStapleStrandCrossover,
    DBAptamerLatchTrigger,
)


class DNAOrigamiRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_campaign(
        self,
        nanorobot_name: str,
        geometry_type: str,
        scaffold_type: str,
        staple_strands_count: int,
        predicted_melting_temp_c: float,
        folding_yield_percent: float,
        cargo_cavity_volume_nm3: float,
        latch_trigger_affinity_nM: float,
    ) -> DBDNAOrigamiDesignCampaign:
        campaign = DBDNAOrigamiDesignCampaign(
            id=uuid.uuid4(),
            nanorobot_name=nanorobot_name,
            geometry_type=geometry_type,
            scaffold_type=scaffold_type,
            staple_strands_count=staple_strands_count,
            predicted_melting_temp_c=predicted_melting_temp_c,
            folding_yield_percent=folding_yield_percent,
            cargo_cavity_volume_nm3=cargo_cavity_volume_nm3,
            latch_trigger_affinity_nM=latch_trigger_affinity_nM,
        )
        self.db.add(campaign)
        await self.db.commit()
        await self.db.refresh(campaign)
        return campaign

    async def add_staple(
        self,
        campaign_id: uuid.UUID,
        strand_index: int,
        sequence_5to3: str,
        length_nt: int,
        tm_celsius: float,
        crossover_count: int,
    ) -> DBStapleStrandCrossover:
        rec = DBStapleStrandCrossover(
            id=uuid.uuid4(),
            campaign_id=campaign_id,
            strand_index=strand_index,
            sequence_5to3=sequence_5to3,
            length_nt=length_nt,
            tm_celsius=tm_celsius,
            crossover_count=crossover_count,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def add_latch(
        self,
        campaign_id: uuid.UUID,
        target_biomarker: str,
        aptamer_sequence: str,
        opening_half_life_min: float,
        selectivity_ratio: float,
    ) -> DBAptamerLatchTrigger:
        rec = DBAptamerLatchTrigger(
            id=uuid.uuid4(),
            campaign_id=campaign_id,
            target_biomarker=target_biomarker,
            aptamer_sequence=aptamer_sequence,
            opening_half_life_min=opening_half_life_min,
            selectivity_ratio=selectivity_ratio,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def get_campaign_with_details(self, campaign_id: uuid.UUID) -> Optional[DBDNAOrigamiDesignCampaign]:
        stmt = (
            select(DBDNAOrigamiDesignCampaign)
            .where(DBDNAOrigamiDesignCampaign.id == campaign_id)
            .options(
                selectinload(DBDNAOrigamiDesignCampaign.staples),
                selectinload(DBDNAOrigamiDesignCampaign.latches),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
