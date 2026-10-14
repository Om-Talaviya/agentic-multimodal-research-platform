"""Repository for Phase 501: Autonomous CRISPR-Associated Transposase (CAST) Targeted Large Genomic Cargo Integrator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cast_transposase_genomic_integration import (
    CastTransposaseGenomicIntegrationStudy,
    CastTransposaseGenomicIntegrationItemProfile,
    CastTransposaseGenomicIntegrationMetricTrace,
)


class CastTransposaseGenomicIntegrationRepository:
    """Database operations for Autonomous CRISPR-Associated Transposase (CAST) Targeted Large Genomic Cargo Integrator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Type V-K CRISPR-Cas12k / TnsA-TnsB-TnsC Transposase Complex with 10kb Cargo Plasmid in Human Cells",
        analytical_modality: str = "cast-transposase-integration",
        targeted_insertion_efficiency_pct: float = 68.5,
        on_target_integration_accuracy_pct: float = 99.2,
        cargo_payload_size_capacity_kb: float = 10.0,
        indel_free_junction_preservation_ratio: float = 0.985,
        confidence_score: float = 0.994,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CastTransposaseGenomicIntegrationStudy:
        study = CastTransposaseGenomicIntegrationStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            targeted_insertion_efficiency_pct=targeted_insertion_efficiency_pct,
            on_target_integration_accuracy_pct=on_target_integration_accuracy_pct,
            cargo_payload_size_capacity_kb=cargo_payload_size_capacity_kb,
            indel_free_junction_preservation_ratio=indel_free_junction_preservation_ratio,
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
    ) -> CastTransposaseGenomicIntegrationItemProfile:
        item = CastTransposaseGenomicIntegrationItemProfile(
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
    ) -> CastTransposaseGenomicIntegrationMetricTrace:
        trace = CastTransposaseGenomicIntegrationMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CastTransposaseGenomicIntegrationStudy]:
        result = await self.session.execute(
            select(CastTransposaseGenomicIntegrationStudy)
            .options(
                selectinload(CastTransposaseGenomicIntegrationStudy.item_profiles),
                selectinload(CastTransposaseGenomicIntegrationStudy.metric_traces),
            )
            .where(CastTransposaseGenomicIntegrationStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[CastTransposaseGenomicIntegrationStudy]:
        result = await self.session.execute(
            select(CastTransposaseGenomicIntegrationStudy)
            .options(
                selectinload(CastTransposaseGenomicIntegrationStudy.item_profiles),
                selectinload(CastTransposaseGenomicIntegrationStudy.metric_traces),
            )
            .order_by(CastTransposaseGenomicIntegrationStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
