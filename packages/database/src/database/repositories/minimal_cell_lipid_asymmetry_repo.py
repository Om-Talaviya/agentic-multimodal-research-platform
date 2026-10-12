"""Repository for Phase 423: Autonomous Synthetic Minimal Cell Membrane Lipid Bilayer Asymmetry & Vesicle Budding Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.minimal_cell_lipid_asymmetry import (
    MinimalCellLipidAsymmetryStudy,
    MinimalCellLipidAsymmetryItemProfile,
    MinimalCellLipidAsymmetryMetricTrace,
)


class MinimalCellLipidAsymmetryRepository:
    """Database operations for Autonomous Synthetic Minimal Cell Membrane Lipid Bilayer Asymmetry & Vesicle Budding Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Synthetic Giant Unilamellar Vesicle (GUV) with Flippase ABCB4",
        analytical_modality: str = "minimal-cell-lipid",
        bilayer_asymmetry_index: float = 0.884,
        membrane_bending_rigidity_kbt: float = 18.2,
        vesicle_budding_rate_um_per_min: float = 0.35,
        inner_leaflet_phosphatidylserine_ratio: float = 0.912,
        confidence_score: float = 0.986,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MinimalCellLipidAsymmetryStudy:
        study = MinimalCellLipidAsymmetryStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            bilayer_asymmetry_index=bilayer_asymmetry_index,
            membrane_bending_rigidity_kbt=membrane_bending_rigidity_kbt,
            vesicle_budding_rate_um_per_min=vesicle_budding_rate_um_per_min,
            inner_leaflet_phosphatidylserine_ratio=inner_leaflet_phosphatidylserine_ratio,
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
    ) -> MinimalCellLipidAsymmetryItemProfile:
        item = MinimalCellLipidAsymmetryItemProfile(
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
    ) -> MinimalCellLipidAsymmetryMetricTrace:
        trace = MinimalCellLipidAsymmetryMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MinimalCellLipidAsymmetryStudy]:
        result = await self.session.execute(
            select(MinimalCellLipidAsymmetryStudy)
            .options(
                selectinload(MinimalCellLipidAsymmetryStudy.item_profiles),
                selectinload(MinimalCellLipidAsymmetryStudy.metric_traces),
            )
            .where(MinimalCellLipidAsymmetryStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[MinimalCellLipidAsymmetryStudy]:
        result = await self.session.execute(
            select(MinimalCellLipidAsymmetryStudy)
            .options(
                selectinload(MinimalCellLipidAsymmetryStudy.item_profiles),
                selectinload(MinimalCellLipidAsymmetryStudy.metric_traces),
            )
            .order_by(MinimalCellLipidAsymmetryStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
