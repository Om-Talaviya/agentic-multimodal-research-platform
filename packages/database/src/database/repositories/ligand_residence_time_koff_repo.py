"""Repository for Phase 422: Autonomous Allosteric Ligand Residence Time & Dissociation Rate Constant (k_off) Molecular Dynamics Extractor."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.ligand_residence_time_koff import (
    LigandResidenceTimeKoffStudy,
    LigandResidenceTimeKoffItemProfile,
    LigandResidenceTimeKoffMetricTrace,
)


class LigandResidenceTimeKoffRepository:
    """Database operations for Autonomous Allosteric Ligand Residence Time & Dissociation Rate Constant (k_off) Molecular Dynamics Extractor."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Kinase Allosteric Pocket with Type II Small Molecule Inhibitor",
        analytical_modality: str = "residence-time-koff",
        unbinding_rate_koff_s_inv: float = 0.0024,
        residence_time_minutes: float = 416.7,
        dissociation_free_energy_barrier_kcal: float = 21.4,
        binding_pocket_hydration_entropy: float = -8.6,
        confidence_score: float = 0.984,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> LigandResidenceTimeKoffStudy:
        study = LigandResidenceTimeKoffStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            unbinding_rate_koff_s_inv=unbinding_rate_koff_s_inv,
            residence_time_minutes=residence_time_minutes,
            dissociation_free_energy_barrier_kcal=dissociation_free_energy_barrier_kcal,
            binding_pocket_hydration_entropy=binding_pocket_hydration_entropy,
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
    ) -> LigandResidenceTimeKoffItemProfile:
        item = LigandResidenceTimeKoffItemProfile(
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
    ) -> LigandResidenceTimeKoffMetricTrace:
        trace = LigandResidenceTimeKoffMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[LigandResidenceTimeKoffStudy]:
        result = await self.session.execute(
            select(LigandResidenceTimeKoffStudy)
            .options(
                selectinload(LigandResidenceTimeKoffStudy.item_profiles),
                selectinload(LigandResidenceTimeKoffStudy.metric_traces),
            )
            .where(LigandResidenceTimeKoffStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[LigandResidenceTimeKoffStudy]:
        result = await self.session.execute(
            select(LigandResidenceTimeKoffStudy)
            .options(
                selectinload(LigandResidenceTimeKoffStudy.item_profiles),
                selectinload(LigandResidenceTimeKoffStudy.metric_traces),
            )
            .order_by(LigandResidenceTimeKoffStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
