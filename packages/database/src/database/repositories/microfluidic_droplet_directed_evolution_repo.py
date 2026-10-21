"""Repository for Phase 577: Autonomous Microfluidic Droplet-Based Directed Evolution & Enzyme Fitness Landscape Navigator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.microfluidic_droplet_directed_evolution import (
    MicrofluidicDropletDirectedEvolutionStudy,
    MicrofluidicDropletDirectedEvolutionItemProfile,
    MicrofluidicDropletDirectedEvolutionMetricTrace,
)


class MicrofluidicDropletDirectedEvolutionRepository:
    """Repository for Autonomous Microfluidic Droplet-Based Directed Evolution & Enzyme Fitness Landscape Navigator storage and retrieval."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str,
        analytical_modality: str,
        droplet_generation_rate_hz: float,
        enzyme_kcat_fold_improvement: float,
        fitness_landscape_ruggedness_index: float,
        epistatic_interaction_coefficient: float,
        confidence_score: float = 0.996,
        status: str = "completed",
        summary_report: Optional[str] = None,
        parameters: Optional[dict] = None,
    ) -> MicrofluidicDropletDirectedEvolutionStudy:
        study = MicrofluidicDropletDirectedEvolutionStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            droplet_generation_rate_hz=droplet_generation_rate_hz,
            enzyme_kcat_fold_improvement=enzyme_kcat_fold_improvement,
            fitness_landscape_ruggedness_index=fitness_landscape_ruggedness_index,
            epistatic_interaction_coefficient=epistatic_interaction_coefficient,
            confidence_score=confidence_score,
            status=status,
            summary_report=summary_report,
            parameters=parameters or {},
        )
        self.session.add(study)
        await self.session.commit()
        await self.session.refresh(study)
        return study

    async def get_study(self, study_id: UUID) -> Optional[MicrofluidicDropletDirectedEvolutionStudy]:
        stmt = select(MicrofluidicDropletDirectedEvolutionStudy).where(MicrofluidicDropletDirectedEvolutionStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[MicrofluidicDropletDirectedEvolutionStudy]:
        stmt = select(MicrofluidicDropletDirectedEvolutionStudy).order_by(MicrofluidicDropletDirectedEvolutionStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_item_profile(
        self,
        study_id: UUID,
        item_name: str,
        quantitative_value: float,
        profile_category: str = "Analysis Profile",
        log2_fold_change: float = 1.5,
        significance_score: float = 0.95,
    ) -> MicrofluidicDropletDirectedEvolutionItemProfile:
        profile = MicrofluidicDropletDirectedEvolutionItemProfile(
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
        p_value: float = 0.05,
    ) -> MicrofluidicDropletDirectedEvolutionMetricTrace:
        trace = MicrofluidicDropletDirectedEvolutionMetricTrace(
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
