"""Repository for Phase 430: Autonomous Targeted Protein Degradation Bifunctional Degron Heterobifunctional Ternary Interface Docking Forecaster."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.bifunctional_degron_ternary_docking import (
    BifunctionalDegronTernaryDockingStudy,
    BifunctionalDegronTernaryDockingItemProfile,
    BifunctionalDegronTernaryDockingMetricTrace,
)


class BifunctionalDegronTernaryDockingRepository:
    """Database operations for Autonomous Targeted Protein Degradation Bifunctional Degron Heterobifunctional Ternary Interface Docking Forecaster."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "VHL-E3 Ligase, Linker, and Target Oncogenic Kinase Complex",
        analytical_modality: str = "bifunctional-degron-docking",
        ternary_complex_cooperativity_alpha: float = 3.42,
        buried_solvent_accessible_surface_angstrom2: float = 1140.0,
        ubiquitination_zone_distance_angstrom: float = 12.8,
        hook_effect_concentration_uM: float = 2.5,
        confidence_score: float = 0.988,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> BifunctionalDegronTernaryDockingStudy:
        study = BifunctionalDegronTernaryDockingStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            ternary_complex_cooperativity_alpha=ternary_complex_cooperativity_alpha,
            buried_solvent_accessible_surface_angstrom2=buried_solvent_accessible_surface_angstrom2,
            ubiquitination_zone_distance_angstrom=ubiquitination_zone_distance_angstrom,
            hook_effect_concentration_uM=hook_effect_concentration_uM,
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
    ) -> BifunctionalDegronTernaryDockingItemProfile:
        item = BifunctionalDegronTernaryDockingItemProfile(
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
    ) -> BifunctionalDegronTernaryDockingMetricTrace:
        trace = BifunctionalDegronTernaryDockingMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[BifunctionalDegronTernaryDockingStudy]:
        result = await self.session.execute(
            select(BifunctionalDegronTernaryDockingStudy)
            .options(
                selectinload(BifunctionalDegronTernaryDockingStudy.item_profiles),
                selectinload(BifunctionalDegronTernaryDockingStudy.metric_traces),
            )
            .where(BifunctionalDegronTernaryDockingStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[BifunctionalDegronTernaryDockingStudy]:
        result = await self.session.execute(
            select(BifunctionalDegronTernaryDockingStudy)
            .options(
                selectinload(BifunctionalDegronTernaryDockingStudy.item_profiles),
                selectinload(BifunctionalDegronTernaryDockingStudy.metric_traces),
            )
            .order_by(BifunctionalDegronTernaryDockingStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
