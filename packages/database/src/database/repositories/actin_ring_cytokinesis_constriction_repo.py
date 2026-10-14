"""Repository for Phase 477: Autonomous Nanoscale Cytoskeletal Actin Ring Constriction & Cytokinesis Cleavage Furrow Modeler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.actin_ring_cytokinesis_constriction import (
    ActinRingCytokinesisConstrictionStudy,
    ActinRingCytokinesisConstrictionItemProfile,
    ActinRingCytokinesisConstrictionMetricTrace,
)


class ActinRingCytokinesisConstrictionRepository:
    """Database operations for Autonomous Nanoscale Cytoskeletal Actin Ring Constriction & Cytokinesis Cleavage Furrow Modeler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Vitrified Dividing S. pombe Protoplast Actomyosin Ring Complex with Myosin-II / Formin Cdc12 Clusters",
        analytical_modality: str = "actin-ring-cytokinesis-constriction",
        contractile_ring_tension_pN: float = 480.0,
        furrow_ingression_velocity_nm_per_s: float = 2.45,
        actin_filament_turnover_rate_s_inv: float = 0.045,
        ring_diameter_constriction_ratio: float = 0.885,
        confidence_score: float = 0.992,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> ActinRingCytokinesisConstrictionStudy:
        study = ActinRingCytokinesisConstrictionStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            contractile_ring_tension_pN=contractile_ring_tension_pN,
            furrow_ingression_velocity_nm_per_s=furrow_ingression_velocity_nm_per_s,
            actin_filament_turnover_rate_s_inv=actin_filament_turnover_rate_s_inv,
            ring_diameter_constriction_ratio=ring_diameter_constriction_ratio,
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
    ) -> ActinRingCytokinesisConstrictionItemProfile:
        item = ActinRingCytokinesisConstrictionItemProfile(
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
    ) -> ActinRingCytokinesisConstrictionMetricTrace:
        trace = ActinRingCytokinesisConstrictionMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[ActinRingCytokinesisConstrictionStudy]:
        result = await self.session.execute(
            select(ActinRingCytokinesisConstrictionStudy)
            .options(
                selectinload(ActinRingCytokinesisConstrictionStudy.item_profiles),
                selectinload(ActinRingCytokinesisConstrictionStudy.metric_traces),
            )
            .where(ActinRingCytokinesisConstrictionStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[ActinRingCytokinesisConstrictionStudy]:
        result = await self.session.execute(
            select(ActinRingCytokinesisConstrictionStudy)
            .options(
                selectinload(ActinRingCytokinesisConstrictionStudy.item_profiles),
                selectinload(ActinRingCytokinesisConstrictionStudy.metric_traces),
            )
            .order_by(ActinRingCytokinesisConstrictionStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
