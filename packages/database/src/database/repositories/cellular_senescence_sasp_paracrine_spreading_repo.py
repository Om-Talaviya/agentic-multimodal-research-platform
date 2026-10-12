"""Repository for Phase 443: Autonomous Cellular Senescence-Associated Secretory Phenotype (SASP) Paracrine Spreading & Tissue Exhaustion Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cellular_senescence_sasp_paracrine_spreading import (
    CellularSenescenceSaspStudy,
    CellularSenescenceSaspItemProfile,
    CellularSenescenceSaspMetricTrace,
)


class CellularSenescenceSaspRepository:
    """Database operations for Autonomous Cellular Senescence-Associated Secretory Phenotype (SASP) Paracrine Spreading & Tissue Exhaustion Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Replicative Senescent Human Dermal Fibroblasts in 3D Collagen Microtissue with Bystander Cells",
        analytical_modality: str = "senescence-sasp-spreading",
        sasp_paracrine_diffusion_radius_um: float = 185.0,
        p16_ink4a_induction_fold_change: float = 5.85,
        bystander_senescence_induction_rate: float = 0.385,
        senolytic_depletion_efficacy_score: float = 0.942,
        confidence_score: float = 0.99,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CellularSenescenceSaspStudy:
        study = CellularSenescenceSaspStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            sasp_paracrine_diffusion_radius_um=sasp_paracrine_diffusion_radius_um,
            p16_ink4a_induction_fold_change=p16_ink4a_induction_fold_change,
            bystander_senescence_induction_rate=bystander_senescence_induction_rate,
            senolytic_depletion_efficacy_score=senolytic_depletion_efficacy_score,
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
    ) -> CellularSenescenceSaspItemProfile:
        item = CellularSenescenceSaspItemProfile(
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
    ) -> CellularSenescenceSaspMetricTrace:
        trace = CellularSenescenceSaspMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CellularSenescenceSaspStudy]:
        result = await self.session.execute(
            select(CellularSenescenceSaspStudy)
            .options(
                selectinload(CellularSenescenceSaspStudy.item_profiles),
                selectinload(CellularSenescenceSaspStudy.metric_traces),
            )
            .where(CellularSenescenceSaspStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[CellularSenescenceSaspStudy]:
        result = await self.session.execute(
            select(CellularSenescenceSaspStudy)
            .options(
                selectinload(CellularSenescenceSaspStudy.item_profiles),
                selectinload(CellularSenescenceSaspStudy.metric_traces),
            )
            .order_by(CellularSenescenceSaspStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
