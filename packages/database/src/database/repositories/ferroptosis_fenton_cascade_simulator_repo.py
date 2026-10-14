"""Repository for Phase 482: Autonomous Cellular Ferroptosis Lipid Peroxidation Fenton Reaction Cascade Simulator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.ferroptosis_fenton_cascade_simulator import (
    FerroptosisFentonCascadeSimulatorStudy,
    FerroptosisFentonCascadeSimulatorItemProfile,
    FerroptosisFentonCascadeSimulatorMetricTrace,
)


class FerroptosisFentonCascadeSimulatorRepository:
    """Database operations for Autonomous Cellular Ferroptosis Lipid Peroxidation Fenton Reaction Cascade Simulator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "GPX4-Inactivated HT-1080 Fibrosarcoma Spheroids with Labile Iron Pool Fe(II) Accumulation",
        analytical_modality: str = "ferroptosis-fenton-cascade",
        lipid_hydroperoxide_accumulation_nmol_mg: float = 34.2,
        labile_iron_pool_chelatable_uM: float = 8.45,
        fenton_reaction_rate_constant_M_inv_s_inv: float = 76.0,
        membrane_permeabilization_lysis_probability: float = 0.945,
        confidence_score: float = 0.99,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> FerroptosisFentonCascadeSimulatorStudy:
        study = FerroptosisFentonCascadeSimulatorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            lipid_hydroperoxide_accumulation_nmol_mg=lipid_hydroperoxide_accumulation_nmol_mg,
            labile_iron_pool_chelatable_uM=labile_iron_pool_chelatable_uM,
            fenton_reaction_rate_constant_M_inv_s_inv=fenton_reaction_rate_constant_M_inv_s_inv,
            membrane_permeabilization_lysis_probability=membrane_permeabilization_lysis_probability,
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
    ) -> FerroptosisFentonCascadeSimulatorItemProfile:
        item = FerroptosisFentonCascadeSimulatorItemProfile(
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
    ) -> FerroptosisFentonCascadeSimulatorMetricTrace:
        trace = FerroptosisFentonCascadeSimulatorMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[FerroptosisFentonCascadeSimulatorStudy]:
        result = await self.session.execute(
            select(FerroptosisFentonCascadeSimulatorStudy)
            .options(
                selectinload(FerroptosisFentonCascadeSimulatorStudy.item_profiles),
                selectinload(FerroptosisFentonCascadeSimulatorStudy.metric_traces),
            )
            .where(FerroptosisFentonCascadeSimulatorStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[FerroptosisFentonCascadeSimulatorStudy]:
        result = await self.session.execute(
            select(FerroptosisFentonCascadeSimulatorStudy)
            .options(
                selectinload(FerroptosisFentonCascadeSimulatorStudy.item_profiles),
                selectinload(FerroptosisFentonCascadeSimulatorStudy.metric_traces),
            )
            .order_by(FerroptosisFentonCascadeSimulatorStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
