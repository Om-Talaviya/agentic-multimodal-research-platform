"""Repository for Phase 437: Autonomous Microbial Electrogenic Biofilm Extracellular Electron Transfer (EET) Simulator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.microbial_electrogenic_biofilm_flux import (
    MicrobialElectrogenicBiofilmStudy,
    MicrobialElectrogenicBiofilmItemProfile,
    MicrobialElectrogenicBiofilmMetricTrace,
)


class MicrobialElectrogenicBiofilmRepository:
    """Database operations for Autonomous Microbial Electrogenic Biofilm Extracellular Electron Transfer (EET) Simulator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Shewanella oneidensis MR-1 Anode Biofilm with Multi-Heme Cytochrome Array",
        analytical_modality: str = "microbial-eet-biofilm",
        current_density_mA_per_cm2: float = 1.42,
        cytochrome_conduction_rate_electrons_per_s: float = 1240.0,
        redox_potential_gradient_mV: float = -280.0,
        biofilm_coulombic_efficiency: float = 0.895,
        confidence_score: float = 0.986,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MicrobialElectrogenicBiofilmStudy:
        study = MicrobialElectrogenicBiofilmStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            current_density_mA_per_cm2=current_density_mA_per_cm2,
            cytochrome_conduction_rate_electrons_per_s=cytochrome_conduction_rate_electrons_per_s,
            redox_potential_gradient_mV=redox_potential_gradient_mV,
            biofilm_coulombic_efficiency=biofilm_coulombic_efficiency,
            confidence_score=confidence_score,
            status=status,
            parameters=parameters or {},
            summary_report=summary_report,
        )
        self.session.add(study)
        await self.session.flush()
        await self.session.refresh(study)
        return study

    async def add_item_profile(
        self,
        study_id: UUID,
        item_name: str,
        profile_category: str = "Analysis Profile",
        quantitative_value: float = 1.0,
        log2_fold_change: float = 1.5,
        significance_score: float = 0.95,
    ) -> MicrobialElectrogenicBiofilmItemProfile:
        item = MicrobialElectrogenicBiofilmItemProfile(
            study_id=study_id,
            item_name=item_name,
            profile_category=profile_category,
            quantitative_value=quantitative_value,
            log2_fold_change=log2_fold_change,
            significance_score=significance_score,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def add_metric_trace(
        self,
        study_id: UUID,
        metric_dimension: str,
        observed_value: float,
        z_score: float = 0.0,
        p_value: float = 0.05,
    ) -> MicrobialElectrogenicBiofilmMetricTrace:
        trace = MicrobialElectrogenicBiofilmMetricTrace(
            study_id=study_id,
            metric_dimension=metric_dimension,
            observed_value=observed_value,
            z_score=z_score,
            p_value=p_value,
        )
        self.session.add(trace)
        await self.session.flush()
        await self.session.refresh(trace)
        return trace

    async def get_study(self, study_id: UUID) -> Optional[MicrobialElectrogenicBiofilmStudy]:
        result = await self.session.execute(
            select(MicrobialElectrogenicBiofilmStudy)
            .options(
                selectinload(MicrobialElectrogenicBiofilmStudy.item_profiles),
                selectinload(MicrobialElectrogenicBiofilmStudy.metric_traces),
            )
            .where(MicrobialElectrogenicBiofilmStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[MicrobialElectrogenicBiofilmStudy]:
        result = await self.session.execute(
            select(MicrobialElectrogenicBiofilmStudy)
            .options(
                selectinload(MicrobialElectrogenicBiofilmStudy.item_profiles),
                selectinload(MicrobialElectrogenicBiofilmStudy.metric_traces),
            )
            .order_by(MicrobialElectrogenicBiofilmStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
