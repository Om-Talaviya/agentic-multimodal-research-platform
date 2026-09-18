"""Repository for Clinical Genomics Digital Twin and Pharmacogenomics."""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.clinical_genomics_twin import (
    DBPatientGenomicProfile,
    DBPharmacogenomicGuideline,
    DBPatientDigitalTwinSim,
)


class ClinicalGenomicsTwinRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_profile(
        self,
        patient_mrn: str,
        age: int = 58,
        sex: str = "FEMALE",
        ancestry: str = "EUROPEAN",
        total_star_alleles_called: int = 6,
        high_risk_drug_interactions_count: int = 2,
        clinical_notes: str = "",
    ) -> DBPatientGenomicProfile:
        profile = DBPatientGenomicProfile(
            patient_mrn=patient_mrn,
            age=age,
            sex=sex,
            ancestry=ancestry,
            total_star_alleles_called=total_star_alleles_called,
            high_risk_drug_interactions_count=high_risk_drug_interactions_count,
            clinical_notes=clinical_notes,
        )
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def add_guideline(
        self,
        profile_id: str,
        gene_symbol: str,
        diplotype_call: str,
        metabolizer_phenotype: str = "INTERMEDIATE_METABOLIZER",
        affected_drug_class: str = "ANTIPLATELET_PRODRUGS",
        cpic_level: str = "LEVEL_A",
        clinical_dose_recommendation: str = "",
    ) -> DBPharmacogenomicGuideline:
        guideline = DBPharmacogenomicGuideline(
            profile_id=profile_id,
            gene_symbol=gene_symbol,
            diplotype_call=diplotype_call,
            metabolizer_phenotype=metabolizer_phenotype,
            affected_drug_class=affected_drug_class,
            cpic_level=cpic_level,
            clinical_dose_recommendation=clinical_dose_recommendation,
        )
        self.session.add(guideline)
        await self.session.commit()
        await self.session.refresh(guideline)
        return guideline

    async def add_twin_simulation(
        self,
        profile_id: str,
        drug_administered: str,
        prescribed_dose_mg: float = 75.0,
        predicted_auc_ratio: float = 0.35,
        toxic_accumulation_risk: str = "LOW",
        recommended_adjusted_dose_mg: float = 0.0,
        alternate_drug_suggestion: str = "Prasugrel or Ticagrelor",
        efficacy_score: float = 0.92,
    ) -> DBPatientDigitalTwinSim:
        sim = DBPatientDigitalTwinSim(
            profile_id=profile_id,
            drug_administered=drug_administered,
            prescribed_dose_mg=prescribed_dose_mg,
            predicted_auc_ratio=predicted_auc_ratio,
            toxic_accumulation_risk=toxic_accumulation_risk,
            recommended_adjusted_dose_mg=recommended_adjusted_dose_mg,
            alternate_drug_suggestion=alternate_drug_suggestion,
            efficacy_score=efficacy_score,
        )
        self.session.add(sim)
        await self.session.commit()
        await self.session.refresh(sim)
        return sim

    async def get_profile(self, profile_id: str) -> Optional[DBPatientGenomicProfile]:
        stmt = (
            select(DBPatientGenomicProfile)
            .where(DBPatientGenomicProfile.id == profile_id)
            .options(
                selectinload(DBPatientGenomicProfile.guidelines),
                selectinload(DBPatientGenomicProfile.twin_simulations),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_profile_by_mrn(self, mrn: str) -> Optional[DBPatientGenomicProfile]:
        stmt = (
            select(DBPatientGenomicProfile)
            .where(DBPatientGenomicProfile.patient_mrn == mrn)
            .options(
                selectinload(DBPatientGenomicProfile.guidelines),
                selectinload(DBPatientGenomicProfile.twin_simulations),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_profiles(self, limit: int = 50) -> List[DBPatientGenomicProfile]:
        stmt = (
            select(DBPatientGenomicProfile)
            .options(
                selectinload(DBPatientGenomicProfile.guidelines),
                selectinload(DBPatientGenomicProfile.twin_simulations),
            )
            .order_by(desc(DBPatientGenomicProfile.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
