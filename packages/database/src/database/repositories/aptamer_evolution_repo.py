"""Repository for Aptamer Evolution (Phase 143)."""

import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.models.aptamer_evolution import (
    DBAptamerEvolutionCampaign,
    DBAptamerRoundSequence,
    DBAptamerTargetBindingRecord,
)


class AptamerEvolutionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_campaign(
        self,
        target_protein_name: str,
        aptamer_type: str,
        initial_pool_size: int,
        selection_rounds: int,
        top_kd_nanomolar: float,
        consensus_motif: str,
    ) -> DBAptamerEvolutionCampaign:
        campaign = DBAptamerEvolutionCampaign(
            target_protein_name=target_protein_name,
            aptamer_type=aptamer_type,
            initial_pool_size=initial_pool_size,
            selection_rounds=selection_rounds,
            top_kd_nanomolar=top_kd_nanomolar,
            consensus_motif=consensus_motif,
        )
        self.db.add(campaign)
        await self.db.commit()
        await self.db.refresh(campaign)
        return campaign

    async def add_round_sequence(
        self,
        campaign_id: uuid.UUID,
        round_number: int,
        sequence_string: str,
        enrichment_fold: float,
        secondary_structure_dot_bracket: str,
        free_energy_kcal_mol: float,
    ) -> DBAptamerRoundSequence:
        seq = DBAptamerRoundSequence(
            campaign_id=campaign_id,
            round_number=round_number,
            sequence_string=sequence_string,
            enrichment_fold=enrichment_fold,
            secondary_structure_dot_bracket=secondary_structure_dot_bracket,
            free_energy_kcal_mol=free_energy_kcal_mol,
        )
        self.db.add(seq)
        await self.db.commit()
        await self.db.refresh(seq)
        return seq

    async def add_binding_record(
        self,
        campaign_id: uuid.UUID,
        aptamer_lead_id: str,
        target_epitope_residues: str,
        kd_nanomolar: float,
        off_target_selectivity_ratio: float,
    ) -> DBAptamerTargetBindingRecord:
        rec = DBAptamerTargetBindingRecord(
            campaign_id=campaign_id,
            aptamer_lead_id=aptamer_lead_id,
            target_epitope_residues=target_epitope_residues,
            kd_nanomolar=kd_nanomolar,
            off_target_selectivity_ratio=off_target_selectivity_ratio,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def get_campaign_with_details(self, campaign_id: uuid.UUID) -> Optional[DBAptamerEvolutionCampaign]:
        stmt = (
            select(DBAptamerEvolutionCampaign)
            .where(DBAptamerEvolutionCampaign.id == campaign_id)
            .options(
                selectinload(DBAptamerEvolutionCampaign.round_sequences),
                selectinload(DBAptamerEvolutionCampaign.binding_records),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
