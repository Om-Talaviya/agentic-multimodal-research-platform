"""Repository for Phase 550: Autonomous High-Throughput Droplet-Based Single-Cell Epigenomic DNA Hydroxymethylation (5hmC) Profiler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.single_cell_5hmc_droplet_profiler import (
    SingleCell5HmcDropletProfilerStudy,
    SingleCell5HmcDropletProfilerItemProfile,
    SingleCell5HmcDropletProfilerMetricTrace,
)


class SingleCell5HmcDropletProfilerRepository:
    """Database operations for Autonomous High-Throughput Droplet-Based Single-Cell Epigenomic DNA Hydroxymethylation (5hmC) Profiler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Single-Cell Microfluidic Barcoded Mouse Hippocampal Neurons subjected to T4 beta-Glucosyltransferase Glucosylation",
        analytical_modality: str = "droplet-epigenomic-5hmc",
        hydroxyl_methylated_cytosine_enrichment_fold: float = 24.6,
        single_cell_epigenomic_capture_efficiency_pct: float = 91.5,
        brain_active_enhancer_5hmc_density_per_kb: float = 4.12,
        enzymatic_glucosylation_stoichiometry_pct: float = 97.8,
        confidence_score: float = 0.996,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SingleCell5HmcDropletProfilerStudy:
        study = SingleCell5HmcDropletProfilerStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            hydroxyl_methylated_cytosine_enrichment_fold=hydroxyl_methylated_cytosine_enrichment_fold,
            single_cell_epigenomic_capture_efficiency_pct=single_cell_epigenomic_capture_efficiency_pct,
            brain_active_enhancer_5hmc_density_per_kb=brain_active_enhancer_5hmc_density_per_kb,
            enzymatic_glucosylation_stoichiometry_pct=enzymatic_glucosylation_stoichiometry_pct,
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
    ) -> SingleCell5HmcDropletProfilerItemProfile:
        item = SingleCell5HmcDropletProfilerItemProfile(
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
    ) -> SingleCell5HmcDropletProfilerMetricTrace:
        trace = SingleCell5HmcDropletProfilerMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SingleCell5HmcDropletProfilerStudy]:
        stmt = (
            select(SingleCell5HmcDropletProfilerStudy)
            .where(SingleCell5HmcDropletProfilerStudy.id == study_id)
            .options(
                selectinload(SingleCell5HmcDropletProfilerStudy.item_profiles),
                selectinload(SingleCell5HmcDropletProfilerStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[SingleCell5HmcDropletProfilerStudy]:
        stmt = (
            select(SingleCell5HmcDropletProfilerStudy)
            .order_by(SingleCell5HmcDropletProfilerStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(SingleCell5HmcDropletProfilerStudy.item_profiles),
                selectinload(SingleCell5HmcDropletProfilerStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
