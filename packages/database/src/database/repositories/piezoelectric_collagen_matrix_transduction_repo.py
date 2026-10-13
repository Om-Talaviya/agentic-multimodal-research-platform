"""Repository for Phase 470: Autonomous Bio-Piezoelectric Collagen Matrix Electromechanical Transduction Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.piezoelectric_collagen_matrix_transduction import (
    PiezoelectricCollagenMatrixTransductionStudy,
    PiezoelectricCollagenMatrixTransductionItemProfile,
    PiezoelectricCollagenMatrixTransductionMetricTrace,
)


class PiezoelectricCollagenMatrixTransductionRepository:
    """Database operations for Autonomous Bio-Piezoelectric Collagen Matrix Electromechanical Transduction Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Dense Fibrillar Type-I Collagen Fascicle Scaffold with Applied High-Frequency Axial Dynamic Strain",
        analytical_modality: str = "piezoelectric-collagen-transduction",
        piezoelectric_coefficient_d33_pC_per_N: float = 8.45,
        surface_potential_streaming_voltage_mV: float = 42.0,
        dynamic_electromechanical_coupling_factor: float = 0.285,
        osteogenic_mineralization_acceleration_index: float = 2.65,
        confidence_score: float = 0.988,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> PiezoelectricCollagenMatrixTransductionStudy:
        study = PiezoelectricCollagenMatrixTransductionStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            piezoelectric_coefficient_d33_pC_per_N=piezoelectric_coefficient_d33_pC_per_N,
            surface_potential_streaming_voltage_mV=surface_potential_streaming_voltage_mV,
            dynamic_electromechanical_coupling_factor=dynamic_electromechanical_coupling_factor,
            osteogenic_mineralization_acceleration_index=osteogenic_mineralization_acceleration_index,
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
    ) -> PiezoelectricCollagenMatrixTransductionItemProfile:
        item = PiezoelectricCollagenMatrixTransductionItemProfile(
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
    ) -> PiezoelectricCollagenMatrixTransductionMetricTrace:
        trace = PiezoelectricCollagenMatrixTransductionMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[PiezoelectricCollagenMatrixTransductionStudy]:
        result = await self.session.execute(
            select(PiezoelectricCollagenMatrixTransductionStudy)
            .options(
                selectinload(PiezoelectricCollagenMatrixTransductionStudy.item_profiles),
                selectinload(PiezoelectricCollagenMatrixTransductionStudy.metric_traces),
            )
            .where(PiezoelectricCollagenMatrixTransductionStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[PiezoelectricCollagenMatrixTransductionStudy]:
        result = await self.session.execute(
            select(PiezoelectricCollagenMatrixTransductionStudy)
            .options(
                selectinload(PiezoelectricCollagenMatrixTransductionStudy.item_profiles),
                selectinload(PiezoelectricCollagenMatrixTransductionStudy.metric_traces),
            )
            .order_by(PiezoelectricCollagenMatrixTransductionStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
