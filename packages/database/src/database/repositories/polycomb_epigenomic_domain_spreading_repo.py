"""Repository for Phase 446: Autonomous Spatial Epigenomic Histone H3K27me3 Polycomb Repressive Domain Spreading Modeler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.polycomb_epigenomic_domain_spreading import (
    PolycombEpigenomicDomainStudy,
    PolycombEpigenomicDomainItemProfile,
    PolycombEpigenomicDomainMetricTrace,
)


class PolycombEpigenomicDomainRepository:
    """Database operations for Autonomous Spatial Epigenomic Histone H3K27me3 Polycomb Repressive Domain Spreading Modeler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Pluripotent Embryonic Stem Cells Differentiation Locus Chromatin Super-Domain",
        analytical_modality: str = "polycomb-epigenomic-spreading",
        polycomb_spreading_velocity_bp_per_hr: float = 1450.0,
        prc2_nucleosome_occupancy_ratio: float = 0.895,
        chromatin_compaction_density_nm: float = 28.4,
        transcriptional_repression_half_life_days: float = 6.8,
        confidence_score: float = 0.988,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> PolycombEpigenomicDomainStudy:
        study = PolycombEpigenomicDomainStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            polycomb_spreading_velocity_bp_per_hr=polycomb_spreading_velocity_bp_per_hr,
            prc2_nucleosome_occupancy_ratio=prc2_nucleosome_occupancy_ratio,
            chromatin_compaction_density_nm=chromatin_compaction_density_nm,
            transcriptional_repression_half_life_days=transcriptional_repression_half_life_days,
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
    ) -> PolycombEpigenomicDomainItemProfile:
        item = PolycombEpigenomicDomainItemProfile(
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
    ) -> PolycombEpigenomicDomainMetricTrace:
        trace = PolycombEpigenomicDomainMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[PolycombEpigenomicDomainStudy]:
        result = await self.session.execute(
            select(PolycombEpigenomicDomainStudy)
            .options(
                selectinload(PolycombEpigenomicDomainStudy.item_profiles),
                selectinload(PolycombEpigenomicDomainStudy.metric_traces),
            )
            .where(PolycombEpigenomicDomainStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[PolycombEpigenomicDomainStudy]:
        result = await self.session.execute(
            select(PolycombEpigenomicDomainStudy)
            .options(
                selectinload(PolycombEpigenomicDomainStudy.item_profiles),
                selectinload(PolycombEpigenomicDomainStudy.metric_traces),
            )
            .order_by(PolycombEpigenomicDomainStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
