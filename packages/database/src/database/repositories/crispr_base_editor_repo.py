"""
Repository for Phase 164: CRISPR Base Editor.
"""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.crispr_base_editor import (
    DBCRISPRBaseEditorStudy,
    DBTargetNucleotideTransition,
    DBBystanderEditingWindow,
)


class CRISPRBaseEditorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_study(
        self,
        target_gene: str,
        editor_type: str,
        protospacer_sequence: str,
        pam_sequence: str,
        on_target_conversion_efficiency: float,
        bystander_purity_score: float,
        indel_frequency_percent: float = 0.05,
        project_id: Optional[uuid.UUID] = None,
    ) -> DBCRISPRBaseEditorStudy:
        study = DBCRISPRBaseEditorStudy(
            target_gene=target_gene,
            editor_type=editor_type,
            protospacer_sequence=protospacer_sequence,
            pam_sequence=pam_sequence,
            on_target_conversion_efficiency=on_target_conversion_efficiency,
            bystander_purity_score=bystander_purity_score,
            indel_frequency_percent=indel_frequency_percent,
            project_id=project_id,
        )
        self.db.add(study)
        await self.db.commit()
        await self.db.refresh(study)
        return study

    async def add_transition(
        self,
        study_id: uuid.UUID,
        protospacer_position: int,
        initial_base: str,
        target_base: str,
        transition_efficiency: float,
        amino_acid_consequence: str,
    ) -> DBTargetNucleotideTransition:
        transition = DBTargetNucleotideTransition(
            study_id=study_id,
            protospacer_position=protospacer_position,
            initial_base=initial_base,
            target_base=target_base,
            transition_efficiency=transition_efficiency,
            amino_acid_consequence=amino_acid_consequence,
        )
        self.db.add(transition)
        await self.db.commit()
        await self.db.refresh(transition)
        return transition

    async def add_bystander_window(
        self,
        study_id: uuid.UUID,
        window_range: str,
        bystander_count: int,
        unintended_mutation_risk_percent: float,
        mitigation_strategy: str,
    ) -> DBBystanderEditingWindow:
        window = DBBystanderEditingWindow(
            study_id=study_id,
            window_range=window_range,
            bystander_count=bystander_count,
            unintended_mutation_risk_percent=unintended_mutation_risk_percent,
            mitigation_strategy=mitigation_strategy,
        )
        self.db.add(window)
        await self.db.commit()
        await self.db.refresh(window)
        return window

    async def get_study(self, study_id: uuid.UUID) -> Optional[DBCRISPRBaseEditorStudy]:
        stmt = (
            select(DBCRISPRBaseEditorStudy)
            .options(
                selectinload(DBCRISPRBaseEditorStudy.transitions),
                selectinload(DBCRISPRBaseEditorStudy.bystander_windows),
            )
            .where(DBCRISPRBaseEditorStudy.id == study_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()
