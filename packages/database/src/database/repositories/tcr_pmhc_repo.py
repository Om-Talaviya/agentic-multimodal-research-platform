"""Repository for TCR-pMHC Affinity (Phase 145)."""

import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.models.tcr_pmhc_affinity import (
    DBTCRpMHCStudy,
    DBTCRCrossReactivityRecord,
)


class TCRpMHCRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_study(
        self,
        tcr_name: str,
        cdr3_alpha_seq: str,
        cdr3_beta_seq: str,
        target_peptide: str,
        hla_allele: str,
        binding_affinity_kd_um: float,
        immunogenicity_score: float,
    ) -> DBTCRpMHCStudy:
        study = DBTCRpMHCStudy(
            tcr_name=tcr_name,
            cdr3_alpha_seq=cdr3_alpha_seq,
            cdr3_beta_seq=cdr3_beta_seq,
            target_peptide=target_peptide,
            hla_allele=hla_allele,
            binding_affinity_kd_um=binding_affinity_kd_um,
            immunogenicity_score=immunogenicity_score,
        )
        self.db.add(study)
        await self.db.commit()
        await self.db.refresh(study)
        return study

    async def add_cross_reactivity_record(
        self,
        study_id: uuid.UUID,
        self_peptide_seq: str,
        tissue_expression: str,
        predicted_cross_kd_um: float,
        off_target_risk_level: str,
    ) -> DBTCRCrossReactivityRecord:
        rec = DBTCRCrossReactivityRecord(
            study_id=study_id,
            self_peptide_seq=self_peptide_seq,
            tissue_expression=tissue_expression,
            predicted_cross_kd_um=predicted_cross_kd_um,
            off_target_risk_level=off_target_risk_level,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def get_study_with_details(self, study_id: uuid.UUID) -> Optional[DBTCRpMHCStudy]:
        stmt = (
            select(DBTCRpMHCStudy)
            .where(DBTCRpMHCStudy.id == study_id)
            .options(selectinload(DBTCRpMHCStudy.cross_reactivity_records))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
