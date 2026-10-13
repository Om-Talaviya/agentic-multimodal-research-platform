"""Repository for Phase 456: Autonomous Morphogen Gradient Diffusion-Turing Pattern Self-Organization Simulator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.morphogen_gradient_turing_pattern import (
    MorphogenGradientTuringPatternStudy,
    MorphogenGradientTuringPatternItemProfile,
    MorphogenGradientTuringPatternMetricTrace,
)


class MorphogenGradientTuringPatternRepository:
    """Database operations for Autonomous Morphogen Gradient Diffusion-Turing Pattern Self-Organization Simulator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Synthetic Multicellular Embryoid with Nodal/Lefty Reaction-Diffusion Pattern Formation",
        analytical_modality: str = "morphogen-turing-morphogenesis",
        turing_instability_wavelength_um: float = 48.2,
        nodal_diffusion_coefficient_um2_per_s: float = 12.4,
        pattern_symmetry_breaking_order_parameter: float = 0.895,
        tissue_axis_polarization_ratio: float = 3.85,
        confidence_score: float = 0.988,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MorphogenGradientTuringPatternStudy:
        study = MorphogenGradientTuringPatternStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            turing_instability_wavelength_um=turing_instability_wavelength_um,
            nodal_diffusion_coefficient_um2_per_s=nodal_diffusion_coefficient_um2_per_s,
            pattern_symmetry_breaking_order_parameter=pattern_symmetry_breaking_order_parameter,
            tissue_axis_polarization_ratio=tissue_axis_polarization_ratio,
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
    ) -> MorphogenGradientTuringPatternItemProfile:
        item = MorphogenGradientTuringPatternItemProfile(
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
    ) -> MorphogenGradientTuringPatternMetricTrace:
        trace = MorphogenGradientTuringPatternMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MorphogenGradientTuringPatternStudy]:
        result = await self.session.execute(
            select(MorphogenGradientTuringPatternStudy)
            .options(
                selectinload(MorphogenGradientTuringPatternStudy.item_profiles),
                selectinload(MorphogenGradientTuringPatternStudy.metric_traces),
            )
            .where(MorphogenGradientTuringPatternStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[MorphogenGradientTuringPatternStudy]:
        result = await self.session.execute(
            select(MorphogenGradientTuringPatternStudy)
            .options(
                selectinload(MorphogenGradientTuringPatternStudy.item_profiles),
                selectinload(MorphogenGradientTuringPatternStudy.metric_traces),
            )
            .order_by(MorphogenGradientTuringPatternStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
