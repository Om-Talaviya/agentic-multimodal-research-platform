"""Repository for mRNA Codon Optimization (Phase 153)."""

import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.mrna_codon_optimization import (
    DBmRNACodonOptimizationCampaign,
    DBOptimizedCodonVariant,
    DBCAIProfilePoint,
)


class mRNACodonRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_campaign(
        self,
        target_protein_name: str,
        expression_host: str,
        original_cai: float,
        optimized_cai: float,
        gc_content_percent: float,
        mfe_secondary_struct_kcal_mol: float,
        uridine_depletion_percent: float,
        translation_efficiency_score: float,
    ) -> DBmRNACodonOptimizationCampaign:
        campaign = DBmRNACodonOptimizationCampaign(
            id=uuid.uuid4(),
            target_protein_name=target_protein_name,
            expression_host=expression_host,
            original_cai=original_cai,
            optimized_cai=optimized_cai,
            gc_content_percent=gc_content_percent,
            mfe_secondary_struct_kcal_mol=mfe_secondary_struct_kcal_mol,
            uridine_depletion_percent=uridine_depletion_percent,
            translation_efficiency_score=translation_efficiency_score,
        )
        self.db.add(campaign)
        await self.db.commit()
        await self.db.refresh(campaign)
        return campaign

    async def add_variant(
        self,
        campaign_id: uuid.UUID,
        variant_rank: int,
        mrna_sequence: str,
        pareto_fitness_score: float,
        ribosome_dwell_time_ms: float,
        immunogenicity_risk_score: float,
    ) -> DBOptimizedCodonVariant:
        rec = DBOptimizedCodonVariant(
            id=uuid.uuid4(),
            campaign_id=campaign_id,
            variant_rank=variant_rank,
            mrna_sequence=mrna_sequence,
            pareto_fitness_score=pareto_fitness_score,
            ribosome_dwell_time_ms=ribosome_dwell_time_ms,
            immunogenicity_risk_score=immunogenicity_risk_score,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def add_cai_point(
        self,
        campaign_id: uuid.UUID,
        codon_position: int,
        codon_triplet: str,
        amino_acid: str,
        relative_adaptiveness: float,
    ) -> DBCAIProfilePoint:
        rec = DBCAIProfilePoint(
            id=uuid.uuid4(),
            campaign_id=campaign_id,
            codon_position=codon_position,
            codon_triplet=codon_triplet,
            amino_acid=amino_acid,
            relative_adaptiveness=relative_adaptiveness,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def get_campaign_with_details(self, campaign_id: uuid.UUID) -> Optional[DBmRNACodonOptimizationCampaign]:
        stmt = (
            select(DBmRNACodonOptimizationCampaign)
            .where(DBmRNACodonOptimizationCampaign.id == campaign_id)
            .options(
                selectinload(DBmRNACodonOptimizationCampaign.variants),
                selectinload(DBmRNACodonOptimizationCampaign.cai_profiles),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
