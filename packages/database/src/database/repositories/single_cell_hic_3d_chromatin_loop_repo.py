"""Repository for Phase 282: Autonomous Single-Cell Chromatin Conformation (scHi-C) 3D Loop & Topologically Associating Domain Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.single_cell_hic_3d_chromatin_loop import (
    SingleCellHic3dChromatinLoopStudy,
    SingleCellHic3dChromatinLoopItemProfile,
    SingleCellHic3dChromatinLoopMetricTrace,
)


class SingleCellHic3dChromatinLoopRepository:
    """Database operations for Autonomous Single-Cell Chromatin Conformation (scHi-C) 3D Loop & Topologically Associating Domain Engine studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "single-cell-hic-3d-chromatin-loop",
        single_cell_tad_boundary_precision_score: float = 95.6,
        chromatin_loop_contact_enrichment_fold: float = 7.4,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SingleCellHic3dChromatinLoopStudy:
        study = SingleCellHic3dChromatinLoopStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            single_cell_tad_boundary_precision_score=single_cell_tad_boundary_precision_score,
            chromatin_loop_contact_enrichment_fold=chromatin_loop_contact_enrichment_fold,
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
    ) -> SingleCellHic3dChromatinLoopItemProfile:
        item = SingleCellHic3dChromatinLoopItemProfile(
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
    ) -> SingleCellHic3dChromatinLoopMetricTrace:
        item = SingleCellHic3dChromatinLoopMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SingleCellHic3dChromatinLoopStudy]:
        stmt = select(SingleCellHic3dChromatinLoopStudy).where(SingleCellHic3dChromatinLoopStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[SingleCellHic3dChromatinLoopStudy]:
        stmt = select(SingleCellHic3dChromatinLoopStudy).order_by(SingleCellHic3dChromatinLoopStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
