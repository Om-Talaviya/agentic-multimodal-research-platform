"""Repository for Phase 435: Autonomous Reconfigurable DNA Origami Dynamic Hinge Compliant Nano-Actuator Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.dna_origami_dynamic_hinge_biosensor import (
    DnaOrigamiDynamicHingeStudy,
    DnaOrigamiDynamicHingeItemProfile,
    DnaOrigamiDynamicHingeMetricTrace,
)


class DnaOrigamiDynamicHingeRepository:
    """Database operations for Autonomous Reconfigurable DNA Origami Dynamic Hinge Compliant Nano-Actuator Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Hexagonal Bundle DNA Origami Nano-Hinge with Fluorophore/Quencher FRET Pair",
        analytical_modality: str = "dna-origami-hinge",
        hinge_flexibility_angle_deg: float = 62.4,
        fret_efficiency_dynamic_ratio: float = 0.865,
        folding_yield_percentage: float = 91.2,
        magnesium_stabilization_mM: float = 12.5,
        confidence_score: float = 0.988,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> DnaOrigamiDynamicHingeStudy:
        study = DnaOrigamiDynamicHingeStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            hinge_flexibility_angle_deg=hinge_flexibility_angle_deg,
            fret_efficiency_dynamic_ratio=fret_efficiency_dynamic_ratio,
            folding_yield_percentage=folding_yield_percentage,
            magnesium_stabilization_mM=magnesium_stabilization_mM,
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
    ) -> DnaOrigamiDynamicHingeItemProfile:
        item = DnaOrigamiDynamicHingeItemProfile(
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
    ) -> DnaOrigamiDynamicHingeMetricTrace:
        trace = DnaOrigamiDynamicHingeMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[DnaOrigamiDynamicHingeStudy]:
        result = await self.session.execute(
            select(DnaOrigamiDynamicHingeStudy)
            .options(
                selectinload(DnaOrigamiDynamicHingeStudy.item_profiles),
                selectinload(DnaOrigamiDynamicHingeStudy.metric_traces),
            )
            .where(DnaOrigamiDynamicHingeStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DnaOrigamiDynamicHingeStudy]:
        result = await self.session.execute(
            select(DnaOrigamiDynamicHingeStudy)
            .options(
                selectinload(DnaOrigamiDynamicHingeStudy.item_profiles),
                selectinload(DnaOrigamiDynamicHingeStudy.metric_traces),
            )
            .order_by(DnaOrigamiDynamicHingeStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
