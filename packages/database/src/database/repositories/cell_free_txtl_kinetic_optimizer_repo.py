"""Repository for Phase 274: Autonomous Cell-Free TX-TL Synthetic Gene Circuit Kinetic Characterization & Metabolic Flux Optimizer."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cell_free_txtl_kinetic_optimizer import (
    CellFreeTxtlKineticOptimizerStudy,
    CellFreeTxtlKineticOptimizerItemProfile,
    CellFreeTxtlKineticOptimizerMetricTrace,
)


class CellFreeTxtlKineticOptimizerRepository:
    """Database operations for Autonomous Cell-Free TX-TL Synthetic Gene Circuit Kinetic Characterization & Metabolic Flux Optimizer studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "cell-free-txtl-kinetic-optimizer",
        txtl_protein_synthesis_yield_ug_mL: float = 480.5,
        resource_depletion_half_life_hours: float = 6.8,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CellFreeTxtlKineticOptimizerStudy:
        study = CellFreeTxtlKineticOptimizerStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            txtl_protein_synthesis_yield_ug_mL=txtl_protein_synthesis_yield_ug_mL,
            resource_depletion_half_life_hours=resource_depletion_half_life_hours,
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
        profile_category: str = "Primary Target",
        quantitative_value: float = 100.0,
        log2_fold_change: float = 1.5,
        significance_score: float = 0.95,
    ) -> CellFreeTxtlKineticOptimizerItemProfile:
        item = CellFreeTxtlKineticOptimizerItemProfile(
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
        z_score: float = 2.1,
        p_value: float = 0.001,
    ) -> CellFreeTxtlKineticOptimizerMetricTrace:
        item = CellFreeTxtlKineticOptimizerMetricTrace(
            study_id=study_id,
            metric_dimension=metric_dimension,
            observed_value=observed_value,
            z_score=z_score,
            p_value=p_value,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_study(self, study_id: UUID) -> Optional[CellFreeTxtlKineticOptimizerStudy]:
        stmt = select(CellFreeTxtlKineticOptimizerStudy).where(CellFreeTxtlKineticOptimizerStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[CellFreeTxtlKineticOptimizerStudy]:
        stmt = select(CellFreeTxtlKineticOptimizerStudy).order_by(CellFreeTxtlKineticOptimizerStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
