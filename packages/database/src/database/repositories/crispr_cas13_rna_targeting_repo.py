"""Repository for Phase 195: CRISPR-Cas13 RNA-Targeting & Collateral Cleavage Suppressor Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.crispr_cas13_rna_targeting import (
    CRISPRCas13RNATargetingStudy,
    CRISPRCas13RNATargetingItemProfile,
    CRISPRCas13RNATargetingMetricTrace,
)


class CRISPRCas13RNATargetingRepository:
    """Database operations for CRISPR-Cas13 RNA-Targeting & Collateral Cleavage Suppressor Engine studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "CRISPR-Cas13 RNA Targeting",
        on_target_rna_knockdown_percent: float = 96.4,
        collateral_rna_suppression_ratio: float = 0.982,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CRISPRCas13RNATargetingStudy:
        study = CRISPRCas13RNATargetingStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            on_target_rna_knockdown_percent=on_target_rna_knockdown_percent,
            collateral_rna_suppression_ratio=collateral_rna_suppression_ratio,
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
    ) -> CRISPRCas13RNATargetingItemProfile:
        item = CRISPRCas13RNATargetingItemProfile(
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
    ) -> CRISPRCas13RNATargetingMetricTrace:
        item = CRISPRCas13RNATargetingMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CRISPRCas13RNATargetingStudy]:
        stmt = select(CRISPRCas13RNATargetingStudy).where(CRISPRCas13RNATargetingStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[CRISPRCas13RNATargetingStudy]:
        stmt = select(CRISPRCas13RNATargetingStudy).order_by(CRISPRCas13RNATargetingStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
