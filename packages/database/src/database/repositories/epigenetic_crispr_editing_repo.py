"""Repository for Epigenetic CRISPR Editing (Phase 159)."""

import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.epigenetic_crispr_editing import (
    DBEpigeneticCRISPREditingStudy,
    DBCpGIslandMethylationProfile,
    DBOffTargetEpigeneticEpimutation,
)


class EpigeneticCRISPRRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_study(
        self,
        target_locus_name: str,
        catalytic_effector: str,
        guide_rna_sequence: str,
        targeted_cpg_count: int,
        target_methylation_change_pct: float,
        transcriptional_repression_log2fc: float,
        mitotic_memory_retention_days: float,
        off_target_epimutation_rate_pct: float,
    ) -> DBEpigeneticCRISPREditingStudy:
        study = DBEpigeneticCRISPREditingStudy(
            id=uuid.uuid4(),
            target_locus_name=target_locus_name,
            catalytic_effector=catalytic_effector,
            guide_rna_sequence=guide_rna_sequence,
            targeted_cpg_count=targeted_cpg_count,
            target_methylation_change_pct=target_methylation_change_pct,
            transcriptional_repression_log2fc=transcriptional_repression_log2fc,
            mitotic_memory_retention_days=mitotic_memory_retention_days,
            off_target_epimutation_rate_pct=off_target_epimutation_rate_pct,
        )
        self.db.add(study)
        await self.db.commit()
        await self.db.refresh(study)
        return study

    async def add_cpg_profile(
        self,
        study_id: uuid.UUID,
        genomic_coordinate_bp: int,
        baseline_methylation_pct: float,
        post_edit_methylation_pct: float,
        bisulfite_read_depth: int,
    ) -> DBCpGIslandMethylationProfile:
        rec = DBCpGIslandMethylationProfile(
            id=uuid.uuid4(),
            study_id=study_id,
            genomic_coordinate_bp=genomic_coordinate_bp,
            baseline_methylation_pct=baseline_methylation_pct,
            post_edit_methylation_pct=post_edit_methylation_pct,
            bisulfite_read_depth=bisulfite_read_depth,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def add_off_target(
        self,
        study_id: uuid.UUID,
        off_target_locus: str,
        mismatch_count: int,
        methylation_drift_pct: float,
        safety_classification: str,
    ) -> DBOffTargetEpigeneticEpimutation:
        rec = DBOffTargetEpigeneticEpimutation(
            id=uuid.uuid4(),
            study_id=study_id,
            off_target_locus=off_target_locus,
            mismatch_count=mismatch_count,
            methylation_drift_pct=methylation_drift_pct,
            safety_classification=safety_classification,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def get_study_with_details(self, study_id: uuid.UUID) -> Optional[DBEpigeneticCRISPREditingStudy]:
        stmt = (
            select(DBEpigeneticCRISPREditingStudy)
            .where(DBEpigeneticCRISPREditingStudy.id == study_id)
            .options(
                selectinload(DBEpigeneticCRISPREditingStudy.cpg_profiles),
                selectinload(DBEpigeneticCRISPREditingStudy.off_targets),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
