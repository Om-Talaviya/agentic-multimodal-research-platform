"""Repository for PROTAC Ternary Complex Kinetics (Phase 156)."""

import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.protac_ternary_complex import (
    DBPROTACTernaryComplexStudy,
    DBE3LigaseBindingProfile,
    DBProteinDegradationKineticPoint,
)


class PROTACKineticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_study(
        self,
        protac_compound_name: str,
        target_protein_name: str,
        e3_ligase_name: str,
        linker_type: str,
        cooperativity_alpha: float,
        dc50_nM: float,
        dmax_percent: float,
        hook_effect_threshold_uM: float,
    ) -> DBPROTACTernaryComplexStudy:
        study = DBPROTACTernaryComplexStudy(
            id=uuid.uuid4(),
            protac_compound_name=protac_compound_name,
            target_protein_name=target_protein_name,
            e3_ligase_name=e3_ligase_name,
            linker_type=linker_type,
            cooperativity_alpha=cooperativity_alpha,
            dc50_nM=dc50_nM,
            dmax_percent=dmax_percent,
            hook_effect_threshold_uM=hook_effect_threshold_uM,
        )
        self.db.add(study)
        await self.db.commit()
        await self.db.refresh(study)
        return study

    async def add_e3_profile(
        self,
        study_id: uuid.UUID,
        domain_type: str,
        kd_binary_nM: float,
        kd_ternary_nM: float,
        delta_g_formation_kcal_mol: float,
    ) -> DBE3LigaseBindingProfile:
        rec = DBE3LigaseBindingProfile(
            id=uuid.uuid4(),
            study_id=study_id,
            domain_type=domain_type,
            kd_binary_nM=kd_binary_nM,
            kd_ternary_nM=kd_ternary_nM,
            delta_g_formation_kcal_mol=delta_g_formation_kcal_mol,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def add_degradation_point(
        self,
        study_id: uuid.UUID,
        protac_dose_nM: float,
        ternary_fraction: float,
        degradation_rate_pct: float,
        ubiquitination_flux: float,
    ) -> DBProteinDegradationKineticPoint:
        rec = DBProteinDegradationKineticPoint(
            id=uuid.uuid4(),
            study_id=study_id,
            protac_dose_nM=protac_dose_nM,
            ternary_fraction=ternary_fraction,
            degradation_rate_pct=degradation_rate_pct,
            ubiquitination_flux=ubiquitination_flux,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def get_study_with_details(self, study_id: uuid.UUID) -> Optional[DBPROTACTernaryComplexStudy]:
        stmt = (
            select(DBPROTACTernaryComplexStudy)
            .where(DBPROTACTernaryComplexStudy.id == study_id)
            .options(
                selectinload(DBPROTACTernaryComplexStudy.e3_profiles),
                selectinload(DBPROTACTernaryComplexStudy.degradation_points),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
