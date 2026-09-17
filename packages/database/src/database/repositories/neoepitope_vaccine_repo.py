from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from database.models.neoepitope_vaccine import (
    DBCancerVaccineDesign,
    DBCandidateNeoepitope,
    DBVaccineAdjuvantSchedule,
)

class NeoepitopeVaccineRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_vaccine_design(
        self,
        patient_id: str,
        tumor_type: str,
        hla_alleles: List[str],
        mrna_construct_sequence: Optional[str] = None,
        polyepitope_junction_cleavability_score: float = 0.88,
        predicted_immunogenicity_index: float = 0.92,
        properties: Optional[Dict[str, Any]] = None,
    ) -> DBCancerVaccineDesign:
        vaccine = DBCancerVaccineDesign(
            patient_id=patient_id,
            tumor_type=tumor_type,
            hla_alleles=hla_alleles or [],
            mrna_construct_sequence=mrna_construct_sequence,
            polyepitope_junction_cleavability_score=polyepitope_junction_cleavability_score,
            predicted_immunogenicity_index=predicted_immunogenicity_index,
            properties=properties or {},
        )
        self.session.add(vaccine)
        await self.session.commit()
        await self.session.refresh(vaccine)
        return vaccine

    async def add_candidate_neoepitope(
        self,
        vaccine_id: str,
        mutated_gene: str,
        mutation_type: str,
        peptide_sequence: str,
        wildtype_sequence: str,
        hla_restriction: str,
        mhc_binding_affinity_ic50_nm: float,
        clonality_vaf_pct: float,
        expression_tpm: float,
        immunogenicity_rank_score: float,
        is_selected_for_vaccine: bool = True,
    ) -> DBCandidateNeoepitope:
        neoepitope = DBCandidateNeoepitope(
            vaccine_id=vaccine_id,
            mutated_gene=mutated_gene,
            mutation_type=mutation_type,
            peptide_sequence=peptide_sequence,
            wildtype_sequence=wildtype_sequence,
            hla_restriction=hla_restriction,
            mhc_binding_affinity_ic50_nm=mhc_binding_affinity_ic50_nm,
            clonality_vaf_pct=clonality_vaf_pct,
            expression_tpm=expression_tpm,
            immunogenicity_rank_score=immunogenicity_rank_score,
            is_selected_for_vaccine=is_selected_for_vaccine,
        )
        self.session.add(neoepitope)
        await self.session.commit()
        await self.session.refresh(neoepitope)
        return neoepitope

    async def add_adjuvant_schedule(
        self,
        vaccine_id: str,
        adjuvant_type: str = "Poly-ICLC",
        dose_schedule_days: Optional[List[int]] = None,
        booster_frequency_weeks: int = 4,
        predicted_cd8_tcell_response_pct: float = 74.5,
    ) -> DBVaccineAdjuvantSchedule:
        schedule = DBVaccineAdjuvantSchedule(
            vaccine_id=vaccine_id,
            adjuvant_type=adjuvant_type,
            dose_schedule_days=dose_schedule_days or [0, 3, 7, 14, 28, 56],
            booster_frequency_weeks=booster_frequency_weeks,
            predicted_cd8_tcell_response_pct=predicted_cd8_tcell_response_pct,
        )
        self.session.add(schedule)
        await self.session.commit()
        await self.session.refresh(schedule)
        return schedule

    async def get_vaccine_design_by_id(self, vaccine_id: str) -> Optional[DBCancerVaccineDesign]:
        stmt = (
            select(DBCancerVaccineDesign)
            .options(
                selectinload(DBCancerVaccineDesign.neoepitopes),
                selectinload(DBCancerVaccineDesign.schedules),
            )
            .where(DBCancerVaccineDesign.id == vaccine_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_vaccine_designs(self, limit: int = 50) -> List[DBCancerVaccineDesign]:
        stmt = (
            select(DBCancerVaccineDesign)
            .options(
                selectinload(DBCancerVaccineDesign.neoepitopes),
                selectinload(DBCancerVaccineDesign.schedules),
            )
            .order_by(DBCancerVaccineDesign.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
