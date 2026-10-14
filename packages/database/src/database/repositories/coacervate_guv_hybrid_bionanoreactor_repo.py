"""Repository for Phase 503: Autonomous Synthetic Protocellular Compartment Membraneless Coacervate-GUV Hybrid Bionanoreactor."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.coacervate_guv_hybrid_bionanoreactor import (
    CoacervateGuvHybridBionanoreactorStudy,
    CoacervateGuvHybridBionanoreactorItemProfile,
    CoacervateGuvHybridBionanoreactorMetricTrace,
)


class CoacervateGuvHybridBionanoreactorRepository:
    """Database operations for Autonomous Synthetic Protocellular Compartment Membraneless Coacervate-GUV Hybrid Bionanoreactor."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Liquid-Liquid Phase Separated Polylysine-ATP Coacervates Encapsulated within POPC/Cholesterol Bilayer GUVs",
        analytical_modality: str = "coacervate-guv-hybrid-reactor",
        enzyme_partition_coefficient_k_partition: float = 38.5,
        internal_substrate_conversion_flux_uM_per_s: float = 12.8,
        membrane_selective_permeation_pore_cutoff_kDa: float = 4.5,
        coacervate_droplet_stability_retention_days: float = 14.0,
        confidence_score: float = 0.993,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CoacervateGuvHybridBionanoreactorStudy:
        study = CoacervateGuvHybridBionanoreactorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            enzyme_partition_coefficient_k_partition=enzyme_partition_coefficient_k_partition,
            internal_substrate_conversion_flux_uM_per_s=internal_substrate_conversion_flux_uM_per_s,
            membrane_selective_permeation_pore_cutoff_kDa=membrane_selective_permeation_pore_cutoff_kDa,
            coacervate_droplet_stability_retention_days=coacervate_droplet_stability_retention_days,
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
    ) -> CoacervateGuvHybridBionanoreactorItemProfile:
        item = CoacervateGuvHybridBionanoreactorItemProfile(
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
    ) -> CoacervateGuvHybridBionanoreactorMetricTrace:
        trace = CoacervateGuvHybridBionanoreactorMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CoacervateGuvHybridBionanoreactorStudy]:
        result = await self.session.execute(
            select(CoacervateGuvHybridBionanoreactorStudy)
            .options(
                selectinload(CoacervateGuvHybridBionanoreactorStudy.item_profiles),
                selectinload(CoacervateGuvHybridBionanoreactorStudy.metric_traces),
            )
            .where(CoacervateGuvHybridBionanoreactorStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[CoacervateGuvHybridBionanoreactorStudy]:
        result = await self.session.execute(
            select(CoacervateGuvHybridBionanoreactorStudy)
            .options(
                selectinload(CoacervateGuvHybridBionanoreactorStudy.item_profiles),
                selectinload(CoacervateGuvHybridBionanoreactorStudy.metric_traces),
            )
            .order_by(CoacervateGuvHybridBionanoreactorStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
