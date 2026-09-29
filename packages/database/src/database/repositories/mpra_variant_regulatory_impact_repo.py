"""Repository for Phase 283: Autonomous Ultra-Deep Massively Parallel Reporter Assay (MPRA) Variant Regulatory Impact Predictor."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.mpra_variant_regulatory_impact import (
    MpraVariantRegulatoryImpactStudy,
    MpraVariantRegulatoryImpactItemProfile,
    MpraVariantRegulatoryImpactMetricTrace,
)


class MpraVariantRegulatoryImpactRepository:
    """Database operations for Autonomous Ultra-Deep Massively Parallel Reporter Assay (MPRA) Variant Regulatory Impact Predictor studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "mpra-variant-regulatory-impact",
        mpra_expression_fold_change_r2: float = 0.91,
        causal_regulatory_variant_detection_power: float = 96.2,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MpraVariantRegulatoryImpactStudy:
        study = MpraVariantRegulatoryImpactStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            mpra_expression_fold_change_r2=mpra_expression_fold_change_r2,
            causal_regulatory_variant_detection_power=causal_regulatory_variant_detection_power,
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
        profile_category: str = "Primary Target",
        quantitative_value: float = 100.0,
        log2_fold_change: float = 1.5,
        significance_score: float = 0.95,
    ) -> MpraVariantRegulatoryImpactItemProfile:
        item = MpraVariantRegulatoryImpactItemProfile(
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
        z_score: float = 2.1,
        p_value: float = 0.001,
    ) -> MpraVariantRegulatoryImpactMetricTrace:
        item = MpraVariantRegulatoryImpactMetricTrace(
            study_id=study_id,
            metric_dimension=metric_dimension,
            observed_value=observed_value,
            z_score=z_score,
            p_value=p_value,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_study(self, study_id: UUID) -> Optional[MpraVariantRegulatoryImpactStudy]:
        stmt = select(MpraVariantRegulatoryImpactStudy).where(MpraVariantRegulatoryImpactStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[MpraVariantRegulatoryImpactStudy]:
        stmt = select(MpraVariantRegulatoryImpactStudy).order_by(MpraVariantRegulatoryImpactStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
