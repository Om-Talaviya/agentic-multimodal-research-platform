"""
Repository for Phase 165: Peptide-Drug Conjugate (PDC) Linker Cleavability.
"""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.pdc_conjugate import (
    DBPDCConjugateStudy,
    DBPeptideLinkerCleavageProfile,
    DBCathepsinBSelectivityAssay,
)


class PDCConjugateRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_study(
        self,
        pdc_name: str,
        homing_peptide_sequence: str,
        linker_type: str,
        cytotoxic_payload: str,
        plasma_stability_half_life_hours: float,
        tumor_cathepsin_cleavage_rate_kcat_km: float,
        therapeutic_index_ratio: float,
        bystander_payload_diffusion_score: float = 0.75,
        project_id: Optional[uuid.UUID] = None,
    ) -> DBPDCConjugateStudy:
        study = DBPDCConjugateStudy(
            pdc_name=pdc_name,
            homing_peptide_sequence=homing_peptide_sequence,
            linker_type=linker_type,
            cytotoxic_payload=cytotoxic_payload,
            plasma_stability_half_life_hours=plasma_stability_half_life_hours,
            tumor_cathepsin_cleavage_rate_kcat_km=tumor_cathepsin_cleavage_rate_kcat_km,
            therapeutic_index_ratio=therapeutic_index_ratio,
            bystander_payload_diffusion_score=bystander_payload_diffusion_score,
            project_id=project_id,
        )
        self.db.add(study)
        await self.db.commit()
        await self.db.refresh(study)
        return study

    async def add_cleavage_profile(
        self,
        study_id: uuid.UUID,
        enzyme_target: str,
        cleavage_efficiency_percent: float,
        incubation_time_minutes: float,
        intact_conjugate_remaining_percent: float,
    ) -> DBPeptideLinkerCleavageProfile:
        profile = DBPeptideLinkerCleavageProfile(
            study_id=study_id,
            enzyme_target=enzyme_target,
            cleavage_efficiency_percent=cleavage_efficiency_percent,
            incubation_time_minutes=incubation_time_minutes,
            intact_conjugate_remaining_percent=intact_conjugate_remaining_percent,
        )
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def add_cathepsin_assay(
        self,
        study_id: uuid.UUID,
        tissue_compartment: str,
        enzymatic_activity_units: float,
        payload_release_velocity_nmol_min: float,
        selectivity_fold_enrichment: float,
    ) -> DBCathepsinBSelectivityAssay:
        assay = DBCathepsinBSelectivityAssay(
            study_id=study_id,
            tissue_compartment=tissue_compartment,
            enzymatic_activity_units=enzymatic_activity_units,
            payload_release_velocity_nmol_min=payload_release_velocity_nmol_min,
            selectivity_fold_enrichment=selectivity_fold_enrichment,
        )
        self.db.add(assay)
        await self.db.commit()
        await self.db.refresh(assay)
        return assay

    async def get_study(self, study_id: uuid.UUID) -> Optional[DBPDCConjugateStudy]:
        stmt = (
            select(DBPDCConjugateStudy)
            .options(
                selectinload(DBPDCConjugateStudy.cleavage_profiles),
                selectinload(DBPDCConjugateStudy.cathepsin_assays),
            )
            .where(DBPDCConjugateStudy.id == study_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()
