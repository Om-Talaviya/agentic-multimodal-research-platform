"""Repository for Phase 534: Autonomous High-Throughput 3D Microfluidic Dielectrophoresis (DEP) Circulating Tumor Cell Sorter."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.microfluidic_cell_sorting_dielectrophoresis import (
    MicrofluidicCellSortingDielectrophoresisStudy,
    MicrofluidicCellSortingDielectrophoresisItemProfile,
    MicrofluidicCellSortingDielectrophoresisMetricTrace,
)


class MicrofluidicCellSortingDielectrophoresisRepository:
    """Database operations for Autonomous High-Throughput 3D Microfluidic Dielectrophoresis (DEP) Circulating Tumor Cell Sorter."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Microfluidic Channel with 3D Quadrupole Electrodes for Label-Free Isolation of Metastatic Breast CTCs",
        analytical_modality: str = "microfluidic-dep-cell-sorting",
        target_cell_recovery_purity_pct: float = 96.8,
        sorting_throughput_cells_per_s: float = 12500.0,
        dielectrophoretic_crossover_frequency_khz: float = 185.0,
        post_sorting_cell_viability_pct: float = 98.2,
        confidence_score: float = 0.994,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MicrofluidicCellSortingDielectrophoresisStudy:
        study = MicrofluidicCellSortingDielectrophoresisStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            target_cell_recovery_purity_pct=target_cell_recovery_purity_pct,
            sorting_throughput_cells_per_s=sorting_throughput_cells_per_s,
            dielectrophoretic_crossover_frequency_khz=dielectrophoretic_crossover_frequency_khz,
            post_sorting_cell_viability_pct=post_sorting_cell_viability_pct,
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
    ) -> MicrofluidicCellSortingDielectrophoresisItemProfile:
        item = MicrofluidicCellSortingDielectrophoresisItemProfile(
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
    ) -> MicrofluidicCellSortingDielectrophoresisMetricTrace:
        trace = MicrofluidicCellSortingDielectrophoresisMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MicrofluidicCellSortingDielectrophoresisStudy]:
        stmt = (
            select(MicrofluidicCellSortingDielectrophoresisStudy)
            .where(MicrofluidicCellSortingDielectrophoresisStudy.id == study_id)
            .options(
                selectinload(MicrofluidicCellSortingDielectrophoresisStudy.item_profiles),
                selectinload(MicrofluidicCellSortingDielectrophoresisStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[MicrofluidicCellSortingDielectrophoresisStudy]:
        stmt = (
            select(MicrofluidicCellSortingDielectrophoresisStudy)
            .order_by(MicrofluidicCellSortingDielectrophoresisStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(MicrofluidicCellSortingDielectrophoresisStudy.item_profiles),
                selectinload(MicrofluidicCellSortingDielectrophoresisStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
