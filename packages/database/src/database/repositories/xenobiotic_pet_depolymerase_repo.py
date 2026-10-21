"""Repository for Phase 578: Autonomous Xenobiotic Polyethylene Terephthalate (PET) Plastic Enzymatic Depolymerase Engineering & Micro-Solvation Energy Forecaster."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.xenobiotic_pet_depolymerase import (
    XenobioticPetDepolymeraseStudy,
    XenobioticPetDepolymeraseItemProfile,
    XenobioticPetDepolymeraseMetricTrace,
)


class XenobioticPetDepolymeraseRepository:
    """Repository for Autonomous Xenobiotic Polyethylene Terephthalate (PET) Plastic Enzymatic Depolymerase Engineering & Micro-Solvation Energy Forecaster storage and retrieval."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_enzyme: str,
        substrate_type: str,
        catalytic_efficiency_kcat_km: float,
        melting_temperature_tm_celsius: float,
        solvation_free_energy_barrier_kcal: float,
        depolymerization_yield_percent: float,
        confidence_score: float = 0.997,
        status: str = "completed",
        summary_report: Optional[str] = None,
        parameters: Optional[dict] = None,
    ) -> XenobioticPetDepolymeraseStudy:
        study = XenobioticPetDepolymeraseStudy(
            name=name,
            target_enzyme=target_enzyme,
            substrate_type=substrate_type,
            catalytic_efficiency_kcat_km=catalytic_efficiency_kcat_km,
            melting_temperature_tm_celsius=melting_temperature_tm_celsius,
            solvation_free_energy_barrier_kcal=solvation_free_energy_barrier_kcal,
            depolymerization_yield_percent=depolymerization_yield_percent,
            confidence_score=confidence_score,
            status=status,
            summary_report=summary_report,
            parameters=parameters or {},
        )
        self.session.add(study)
        await self.session.commit()
        await self.session.refresh(study)
        return study

    async def get_study(self, study_id: UUID) -> Optional[XenobioticPetDepolymeraseStudy]:
        stmt = select(XenobioticPetDepolymeraseStudy).where(XenobioticPetDepolymeraseStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[XenobioticPetDepolymeraseStudy]:
        stmt = select(XenobioticPetDepolymeraseStudy).order_by(XenobioticPetDepolymeraseStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_item_profile(
        self,
        study_id: UUID,
        item_name: str,
        quantitative_value: float,
        profile_category: str = "Catalytic Subsite",
        log2_fold_change: float = 1.8,
        significance_score: float = 0.96,
    ) -> XenobioticPetDepolymeraseItemProfile:
        profile = XenobioticPetDepolymeraseItemProfile(
            study_id=study_id,
            item_name=item_name,
            profile_category=profile_category,
            quantitative_value=quantitative_value,
            log2_fold_change=log2_fold_change,
            significance_score=significance_score,
        )
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def add_metric_trace(
        self,
        study_id: UUID,
        metric_dimension: str,
        observed_value: float,
        z_score: float = 0.0,
        p_value: float = 0.01,
    ) -> XenobioticPetDepolymeraseMetricTrace:
        trace = XenobioticPetDepolymeraseMetricTrace(
            study_id=study_id,
            metric_dimension=metric_dimension,
            observed_value=observed_value,
            z_score=z_score,
            p_value=p_value,
        )
        self.session.add(trace)
        await self.session.commit()
        await self.session.refresh(trace)
        return trace
