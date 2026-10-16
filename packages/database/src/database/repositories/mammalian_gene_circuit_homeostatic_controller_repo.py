"""Repository for Phase 556: Autonomous Synthetic Mammalian Gene Circuit Feedback Integral Controller for Homeostatic Glucose Regulation."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.mammalian_gene_circuit_homeostatic_controller import (
    MammalianGeneCircuitHomeostaticControllerStudy,
    MammalianGeneCircuitHomeostaticControllerItemProfile,
    MammalianGeneCircuitHomeostaticControllerMetricTrace,
)


class MammalianGeneCircuitHomeostaticControllerRepository:
    """Database operations for Autonomous Synthetic Mammalian Gene Circuit Feedback Integral Controller for Homeostatic Glucose Regulation."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Engineered Beta-Cell Like HEK-293T cells expressing Synthetic Glucose-Sensing Integral Antithetic Feedback Invertible Controller",
        analytical_modality: str = "synthetic-homeostatic-circuit",
        homeostatic_glucose_setpoint_steady_state_mg_dl: float = 95.0,
        integral_control_settling_time_minutes: float = 42.0,
        steady_state_error_offset_pct: float = 0.45,
        insulin_secretion_burst_amplitude_pg_cell: float = 18.2,
        confidence_score: float = 0.998,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MammalianGeneCircuitHomeostaticControllerStudy:
        study = MammalianGeneCircuitHomeostaticControllerStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            homeostatic_glucose_setpoint_steady_state_mg_dl=homeostatic_glucose_setpoint_steady_state_mg_dl,
            integral_control_settling_time_minutes=integral_control_settling_time_minutes,
            steady_state_error_offset_pct=steady_state_error_offset_pct,
            insulin_secretion_burst_amplitude_pg_cell=insulin_secretion_burst_amplitude_pg_cell,
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
    ) -> MammalianGeneCircuitHomeostaticControllerItemProfile:
        item = MammalianGeneCircuitHomeostaticControllerItemProfile(
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
    ) -> MammalianGeneCircuitHomeostaticControllerMetricTrace:
        trace = MammalianGeneCircuitHomeostaticControllerMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MammalianGeneCircuitHomeostaticControllerStudy]:
        stmt = (
            select(MammalianGeneCircuitHomeostaticControllerStudy)
            .where(MammalianGeneCircuitHomeostaticControllerStudy.id == study_id)
            .options(
                selectinload(MammalianGeneCircuitHomeostaticControllerStudy.item_profiles),
                selectinload(MammalianGeneCircuitHomeostaticControllerStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[MammalianGeneCircuitHomeostaticControllerStudy]:
        stmt = (
            select(MammalianGeneCircuitHomeostaticControllerStudy)
            .order_by(MammalianGeneCircuitHomeostaticControllerStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(MammalianGeneCircuitHomeostaticControllerStudy.item_profiles),
                selectinload(MammalianGeneCircuitHomeostaticControllerStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
