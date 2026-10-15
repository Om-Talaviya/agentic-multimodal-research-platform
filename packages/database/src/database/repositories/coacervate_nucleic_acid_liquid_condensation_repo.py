"""Repository for Phase 527: Autonomous Membraneless Coacervate RNA Condensation & Ribozyme Catalytic Acceleration Modeler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.coacervate_nucleic_acid_liquid_condensation import (
    CoacervateNucleicAcidLiquidCondensationStudy,
    CoacervateNucleicAcidLiquidCondensationItemProfile,
    CoacervateNucleicAcidLiquidCondensationMetricTrace,
)


class CoacervateNucleicAcidLiquidCondensationRepository:
    """Database operations for Autonomous Membraneless Coacervate RNA Condensation & Ribozyme Catalytic Acceleration Modeler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Polycationic Polylysine-Spermidine Complex Coacervate Droplet Encapsulating Hammerhead Ribozymes",
        analytical_modality: str = "coacervate-rna-condensation",
        ribozyme_cleavage_rate_enhancement_fold: float = 48.0,
        partition_coefficient_k_partition: float = 125.0,
        droplet_interfacial_surface_tension_uN_m: float = 0.85,
        critical_coacervation_transition_temp_c: float = 37.2,
        confidence_score: float = 0.994,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CoacervateNucleicAcidLiquidCondensationStudy:
        study = CoacervateNucleicAcidLiquidCondensationStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            ribozyme_cleavage_rate_enhancement_fold=ribozyme_cleavage_rate_enhancement_fold,
            partition_coefficient_k_partition=partition_coefficient_k_partition,
            droplet_interfacial_surface_tension_uN_m=droplet_interfacial_surface_tension_uN_m,
            critical_coacervation_transition_temp_c=critical_coacervation_transition_temp_c,
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
    ) -> CoacervateNucleicAcidLiquidCondensationItemProfile:
        item = CoacervateNucleicAcidLiquidCondensationItemProfile(
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
    ) -> CoacervateNucleicAcidLiquidCondensationMetricTrace:
        trace = CoacervateNucleicAcidLiquidCondensationMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CoacervateNucleicAcidLiquidCondensationStudy]:
        stmt = (
            select(CoacervateNucleicAcidLiquidCondensationStudy)
            .where(CoacervateNucleicAcidLiquidCondensationStudy.id == study_id)
            .options(
                selectinload(CoacervateNucleicAcidLiquidCondensationStudy.item_profiles),
                selectinload(CoacervateNucleicAcidLiquidCondensationStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[CoacervateNucleicAcidLiquidCondensationStudy]:
        stmt = (
            select(CoacervateNucleicAcidLiquidCondensationStudy)
            .order_by(CoacervateNucleicAcidLiquidCondensationStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(CoacervateNucleicAcidLiquidCondensationStudy.item_profiles),
                selectinload(CoacervateNucleicAcidLiquidCondensationStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
