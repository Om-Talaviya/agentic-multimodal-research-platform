"""Repository for Phase 555: Autonomous Microfluidic High-Pressure Supercritical Fluid Nanoparticle Encapsulation Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.supercritical_fluid_nanoparticle_encapsulation import (
    SupercriticalFluidNanoparticleEncapsulationStudy,
    SupercriticalFluidNanoparticleEncapsulationItemProfile,
    SupercriticalFluidNanoparticleEncapsulationMetricTrace,
)


class SupercriticalFluidNanoparticleEncapsulationRepository:
    """Database operations for Autonomous Microfluidic High-Pressure Supercritical Fluid Nanoparticle Encapsulation Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Supercritical CO2 Rapid Expansion (RESS-SC) of PLGA-PEG Encapsulating Hydrophobic Paclitaxel and Cy5.5 Nanotracers",
        analytical_modality: str = "supercritical-fluid-nanoparticle",
        nanoparticle_mean_hydrodynamic_diameter_nm: float = 68.5,
        encapsulation_efficiency_payload_pct: float = 94.2,
        polydispersity_index_pdi: float = 0.082,
        supercritical_operating_pressure_bar: float = 185.0,
        confidence_score: float = 0.995,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SupercriticalFluidNanoparticleEncapsulationStudy:
        study = SupercriticalFluidNanoparticleEncapsulationStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            nanoparticle_mean_hydrodynamic_diameter_nm=nanoparticle_mean_hydrodynamic_diameter_nm,
            encapsulation_efficiency_payload_pct=encapsulation_efficiency_payload_pct,
            polydispersity_index_pdi=polydispersity_index_pdi,
            supercritical_operating_pressure_bar=supercritical_operating_pressure_bar,
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
    ) -> SupercriticalFluidNanoparticleEncapsulationItemProfile:
        item = SupercriticalFluidNanoparticleEncapsulationItemProfile(
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
    ) -> SupercriticalFluidNanoparticleEncapsulationMetricTrace:
        trace = SupercriticalFluidNanoparticleEncapsulationMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SupercriticalFluidNanoparticleEncapsulationStudy]:
        stmt = (
            select(SupercriticalFluidNanoparticleEncapsulationStudy)
            .where(SupercriticalFluidNanoparticleEncapsulationStudy.id == study_id)
            .options(
                selectinload(SupercriticalFluidNanoparticleEncapsulationStudy.item_profiles),
                selectinload(SupercriticalFluidNanoparticleEncapsulationStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[SupercriticalFluidNanoparticleEncapsulationStudy]:
        stmt = (
            select(SupercriticalFluidNanoparticleEncapsulationStudy)
            .order_by(SupercriticalFluidNanoparticleEncapsulationStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(SupercriticalFluidNanoparticleEncapsulationStudy.item_profiles),
                selectinload(SupercriticalFluidNanoparticleEncapsulationStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
