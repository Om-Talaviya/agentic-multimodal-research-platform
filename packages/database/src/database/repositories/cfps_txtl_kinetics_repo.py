"""Repository for Cell-Free Protein Synthesis TX-TL (Phase 157)."""

import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.cfps_txtl_kinetics import (
    DBCFPSTXTLKineticsStudy,
    DBRibosomeTranslationalYieldCurve,
    DBMetabolicSubstrateDepletionRecord,
)


class CFPSTXTLRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_study(
        self,
        target_protein_name: str,
        extract_system_type: str,
        reaction_mode: str,
        reaction_time_hours: float,
        final_protein_yield_mg_ml: float,
        transcription_rate_nt_s: float,
        translation_rate_aa_s: float,
        energy_regeneration_efficiency: float,
    ) -> DBCFPSTXTLKineticsStudy:
        study = DBCFPSTXTLKineticsStudy(
            id=uuid.uuid4(),
            target_protein_name=target_protein_name,
            extract_system_type=extract_system_type,
            reaction_mode=reaction_mode,
            reaction_time_hours=reaction_time_hours,
            final_protein_yield_mg_ml=final_protein_yield_mg_ml,
            transcription_rate_nt_s=transcription_rate_nt_s,
            translation_rate_aa_s=translation_rate_aa_s,
            energy_regeneration_efficiency=energy_regeneration_efficiency,
        )
        self.db.add(study)
        await self.db.commit()
        await self.db.refresh(study)
        return study

    async def add_yield_curve_point(
        self,
        study_id: uuid.UUID,
        time_elapsed_hours: float,
        mrna_concentration_uM: float,
        protein_concentration_mg_ml: float,
        ribosome_active_fraction: float,
    ) -> DBRibosomeTranslationalYieldCurve:
        rec = DBRibosomeTranslationalYieldCurve(
            id=uuid.uuid4(),
            study_id=study_id,
            time_elapsed_hours=time_elapsed_hours,
            mrna_concentration_uM=mrna_concentration_uM,
            protein_concentration_mg_ml=protein_concentration_mg_ml,
            ribosome_active_fraction=ribosome_active_fraction,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def add_substrate_depletion(
        self,
        study_id: uuid.UUID,
        substrate_name: str,
        initial_concentration_mM: float,
        final_concentration_mM: float,
        consumption_rate_mM_h: float,
    ) -> DBMetabolicSubstrateDepletionRecord:
        rec = DBMetabolicSubstrateDepletionRecord(
            id=uuid.uuid4(),
            study_id=study_id,
            substrate_name=substrate_name,
            initial_concentration_mM=initial_concentration_mM,
            final_concentration_mM=final_concentration_mM,
            consumption_rate_mM_h=consumption_rate_mM_h,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def get_study_with_details(self, study_id: uuid.UUID) -> Optional[DBCFPSTXTLKineticsStudy]:
        stmt = (
            select(DBCFPSTXTLKineticsStudy)
            .where(DBCFPSTXTLKineticsStudy.id == study_id)
            .options(
                selectinload(DBCFPSTXTLKineticsStudy.yield_curves),
                selectinload(DBCFPSTXTLKineticsStudy.substrates),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
