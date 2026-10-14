"""Repository for Phase 504: Autonomous High-Throughput Droplet Microfluidic Ultra-Fast Directed Enzyme Evolution Kinetic Screener."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.droplet_microfluidic_enzyme_evolution import (
    DropletMicrofluidicEnzymeEvolutionStudy,
    DropletMicrofluidicEnzymeEvolutionItemProfile,
    DropletMicrofluidicEnzymeEvolutionMetricTrace,
)


class DropletMicrofluidicEnzymeEvolutionRepository:
    """Database operations for Autonomous High-Throughput Droplet Microfluidic Ultra-Fast Directed Enzyme Evolution Kinetic Screener."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Picoliter Droplet Emulsion Library of Variant PETase Esterases with Fluorescent Fluorogenic Substrates",
        analytical_modality: str = "droplet-microfluidic-enzyme-screening",
        catalytic_efficiency_improvement_fold: float = 14.8,
        screening_throughput_droplets_per_second: float = 2500.0,
        false_discovery_rate_q_value: float = 0.0015,
        thermostability_delta_tm_celsius: float = 8.5,
        confidence_score: float = 0.996,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> DropletMicrofluidicEnzymeEvolutionStudy:
        study = DropletMicrofluidicEnzymeEvolutionStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            catalytic_efficiency_improvement_fold=catalytic_efficiency_improvement_fold,
            screening_throughput_droplets_per_second=screening_throughput_droplets_per_second,
            false_discovery_rate_q_value=false_discovery_rate_q_value,
            thermostability_delta_tm_celsius=thermostability_delta_tm_celsius,
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
    ) -> DropletMicrofluidicEnzymeEvolutionItemProfile:
        item = DropletMicrofluidicEnzymeEvolutionItemProfile(
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
    ) -> DropletMicrofluidicEnzymeEvolutionMetricTrace:
        trace = DropletMicrofluidicEnzymeEvolutionMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[DropletMicrofluidicEnzymeEvolutionStudy]:
        result = await self.session.execute(
            select(DropletMicrofluidicEnzymeEvolutionStudy)
            .options(
                selectinload(DropletMicrofluidicEnzymeEvolutionStudy.item_profiles),
                selectinload(DropletMicrofluidicEnzymeEvolutionStudy.metric_traces),
            )
            .where(DropletMicrofluidicEnzymeEvolutionStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DropletMicrofluidicEnzymeEvolutionStudy]:
        result = await self.session.execute(
            select(DropletMicrofluidicEnzymeEvolutionStudy)
            .options(
                selectinload(DropletMicrofluidicEnzymeEvolutionStudy.item_profiles),
                selectinload(DropletMicrofluidicEnzymeEvolutionStudy.metric_traces),
            )
            .order_by(DropletMicrofluidicEnzymeEvolutionStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
