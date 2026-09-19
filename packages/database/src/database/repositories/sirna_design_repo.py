"""Repository for siRNA & Oligonucleotide Therapeutic Designer (Phase 98)."""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.models.sirna_design import (
    DBSiRnaDesign,
    DBSiRnaOffTargetHit,
    DBChemicalModificationPattern,
)


class SiRnaDesignRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_design(
        self,
        workspace_id: uuid.UUID,
        target_gene: str,
        sense_sequence: str,
        antisense_sequence: str,
        knockdown_potency_score: float = 93.4,
        on_target_efficiency_score: float = 89.2,
        thermodynamic_end_asymmetry: float = -3.2,
        tlr_immunogenicity_risk: str = "LOW",
        off_target_safety_score: float = 95.8,
        design_metadata: Optional[Dict[str, Any]] = None,
    ) -> DBSiRnaDesign:
        design = DBSiRnaDesign(
            workspace_id=workspace_id,
            target_gene=target_gene,
            sense_sequence=sense_sequence,
            antisense_sequence=antisense_sequence,
            knockdown_potency_score=knockdown_potency_score,
            on_target_efficiency_score=on_target_efficiency_score,
            thermodynamic_end_asymmetry=thermodynamic_end_asymmetry,
            tlr_immunogenicity_risk=tlr_immunogenicity_risk,
            off_target_safety_score=off_target_safety_score,
            design_metadata=design_metadata or {},
        )
        self.session.add(design)
        await self.session.commit()
        await self.session.refresh(design)
        return design

    async def add_off_target_hit(
        self,
        design_id: uuid.UUID,
        off_target_gene: str,
        transcript_id: str,
        seed_region_mismatches: int = 1,
        total_mismatches: int = 3,
        predicted_repression_pct: float = 4.2,
        risk_tier: str = "NEGLIGIBLE",
    ) -> DBSiRnaOffTargetHit:
        hit = DBSiRnaOffTargetHit(
            design_id=design_id,
            off_target_gene=off_target_gene,
            transcript_id=transcript_id,
            seed_region_mismatches=seed_region_mismatches,
            total_mismatches=total_mismatches,
            predicted_repression_pct=predicted_repression_pct,
            risk_tier=risk_tier,
        )
        self.session.add(hit)
        await self.session.commit()
        await self.session.refresh(hit)
        return hit

    async def add_modification(
        self,
        design_id: uuid.UUID,
        strand: str,
        position: int,
        modification_type: str = "2_O_METHYL",
        nuclease_stability_factor: float = 12.5,
    ) -> DBChemicalModificationPattern:
        mod = DBChemicalModificationPattern(
            design_id=design_id,
            strand=strand,
            position=position,
            modification_type=modification_type,
            nuclease_stability_factor=nuclease_stability_factor,
        )
        self.session.add(mod)
        await self.session.commit()
        await self.session.refresh(mod)
        return mod

    async def get_design(self, design_id: uuid.UUID) -> Optional[DBSiRnaDesign]:
        stmt = (
            select(DBSiRnaDesign)
            .options(
                selectinload(DBSiRnaDesign.off_target_hits),
                selectinload(DBSiRnaDesign.modifications),
            )
            .where(DBSiRnaDesign.id == design_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
