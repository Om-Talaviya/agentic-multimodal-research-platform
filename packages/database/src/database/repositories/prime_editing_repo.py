"""Repository for CRISPR Prime & Base Editing data access (Phase 101)."""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.models.prime_editing import (
    DBPrimeEditingDesign,
    DBPegRnaCandidate,
    DBBystanderEditingAlert,
)


class PrimeEditingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_design(
        self,
        workspace_id: uuid.UUID,
        target_gene: str,
        genomic_locus: str,
        intended_edit_type: str,
        editor_architecture: str = "PEmax_PE3",
        predicted_editing_efficiency_pct: float = 64.8,
        purity_score_pct: float = 92.5,
        indel_frequency_pct: float = 1.8,
        design_metadata: Optional[Dict[str, Any]] = None,
    ) -> DBPrimeEditingDesign:
        design = DBPrimeEditingDesign(
            workspace_id=workspace_id,
            target_gene=target_gene,
            genomic_locus=genomic_locus,
            intended_edit_type=intended_edit_type,
            editor_architecture=editor_architecture,
            predicted_editing_efficiency_pct=predicted_editing_efficiency_pct,
            purity_score_pct=purity_score_pct,
            indel_frequency_pct=indel_frequency_pct,
            design_metadata=design_metadata or {},
        )
        self.session.add(design)
        await self.session.commit()
        await self.session.refresh(design)
        return design

    async def add_pegrna_candidate(
        self,
        design_id: uuid.UUID,
        spacer_sequence: str,
        pbs_sequence: str,
        pbs_length_nt: int,
        pbs_tm_celsius: float,
        rtt_sequence: str,
        rtt_length_nt: int,
        nicking_guide_spacer: Optional[str] = None,
        candidate_rank: int = 1,
    ) -> DBPegRnaCandidate:
        candidate = DBPegRnaCandidate(
            design_id=design_id,
            spacer_sequence=spacer_sequence,
            pbs_sequence=pbs_sequence,
            pbs_length_nt=pbs_length_nt,
            pbs_tm_celsius=pbs_tm_celsius,
            rtt_sequence=rtt_sequence,
            rtt_length_nt=rtt_length_nt,
            nicking_guide_spacer=nicking_guide_spacer,
            candidate_rank=candidate_rank,
        )
        self.session.add(candidate)
        await self.session.commit()
        await self.session.refresh(candidate)
        return candidate

    async def add_bystander_alert(
        self,
        design_id: uuid.UUID,
        position_in_window: int,
        bystander_base: str,
        deamination_risk_score: float,
        synonymous_flag: str = "MISSENSE_MUTATION",
    ) -> DBBystanderEditingAlert:
        alert = DBBystanderEditingAlert(
            design_id=design_id,
            position_in_window=position_in_window,
            bystander_base=bystander_base,
            deamination_risk_score=deamination_risk_score,
            synonymous_flag=synonymous_flag,
        )
        self.session.add(alert)
        await self.session.commit()
        await self.session.refresh(alert)
        return alert

    async def get_design(self, design_id: uuid.UUID) -> Optional[DBPrimeEditingDesign]:
        stmt = (
            select(DBPrimeEditingDesign)
            .options(
                selectinload(DBPrimeEditingDesign.pegrna_candidates),
                selectinload(DBPrimeEditingDesign.bystander_alerts),
            )
            .where(DBPrimeEditingDesign.id == design_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
