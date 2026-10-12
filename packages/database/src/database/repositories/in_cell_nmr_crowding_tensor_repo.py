"""Repository for Phase 419: Autonomous In-Cell NMR Macromolecular Crowding & Chemical Shift Perturbation Tensor Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.in_cell_nmr_crowding_tensor import (
    InCellNmrCrowdingTensorStudy,
    InCellNmrCrowdingTensorItemProfile,
    InCellNmrCrowdingTensorMetricTrace,
)


class InCellNmrCrowdingTensorRepository:
    """Database operations for Autonomous In-Cell NMR Macromolecular Crowding & Chemical Shift Perturbation Tensor Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "15N/13C-Enriched Intact E. coli Cytoplasm with Model Protein",
        analytical_modality: str = "in-cell-nmr",
        chemical_shift_perturbation_ppm: float = 0.142,
        rotational_correlation_time_ns: float = 18.4,
        crowding_viscosity_factor: float = 2.85,
        transverse_relaxation_r2_rate: float = 32.1,
        confidence_score: float = 0.982,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> InCellNmrCrowdingTensorStudy:
        study = InCellNmrCrowdingTensorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            chemical_shift_perturbation_ppm=chemical_shift_perturbation_ppm,
            rotational_correlation_time_ns=rotational_correlation_time_ns,
            crowding_viscosity_factor=crowding_viscosity_factor,
            transverse_relaxation_r2_rate=transverse_relaxation_r2_rate,
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
    ) -> InCellNmrCrowdingTensorItemProfile:
        item = InCellNmrCrowdingTensorItemProfile(
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
    ) -> InCellNmrCrowdingTensorMetricTrace:
        trace = InCellNmrCrowdingTensorMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[InCellNmrCrowdingTensorStudy]:
        result = await self.session.execute(
            select(InCellNmrCrowdingTensorStudy)
            .options(
                selectinload(InCellNmrCrowdingTensorStudy.item_profiles),
                selectinload(InCellNmrCrowdingTensorStudy.metric_traces),
            )
            .where(InCellNmrCrowdingTensorStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[InCellNmrCrowdingTensorStudy]:
        result = await self.session.execute(
            select(InCellNmrCrowdingTensorStudy)
            .options(
                selectinload(InCellNmrCrowdingTensorStudy.item_profiles),
                selectinload(InCellNmrCrowdingTensorStudy.metric_traces),
            )
            .order_by(InCellNmrCrowdingTensorStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
