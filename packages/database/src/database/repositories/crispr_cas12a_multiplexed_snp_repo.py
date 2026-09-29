"""Repository for Phase 291: Autonomous CRISPR-Cas12a (Cpf1) Multiplexed Trans-Cleavage Single-Nucleotide Polymorphism Sentinel."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.crispr_cas12a_multiplexed_snp import (
    CrisprCas12aMultiplexedSnpStudy,
    CrisprCas12aMultiplexedSnpItemProfile,
    CrisprCas12aMultiplexedSnpMetricTrace,
)


class CrisprCas12aMultiplexedSnpRepository:
    """Database operations for Autonomous CRISPR-Cas12a (Cpf1) Multiplexed Trans-Cleavage Single-Nucleotide Polymorphism Sentinel studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "crispr-cas12a-multiplexed-snp",
        single_nucleotide_discrimination_ratio: float = 56.4,
        ssdna_trans_cleavage_rate_kcat_km: float = 14000000.0,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CrisprCas12aMultiplexedSnpStudy:
        study = CrisprCas12aMultiplexedSnpStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            single_nucleotide_discrimination_ratio=single_nucleotide_discrimination_ratio,
            ssdna_trans_cleavage_rate_kcat_km=ssdna_trans_cleavage_rate_kcat_km,
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
    ) -> CrisprCas12aMultiplexedSnpItemProfile:
        item = CrisprCas12aMultiplexedSnpItemProfile(
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
    ) -> CrisprCas12aMultiplexedSnpMetricTrace:
        item = CrisprCas12aMultiplexedSnpMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CrisprCas12aMultiplexedSnpStudy]:
        stmt = select(CrisprCas12aMultiplexedSnpStudy).where(CrisprCas12aMultiplexedSnpStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[CrisprCas12aMultiplexedSnpStudy]:
        stmt = select(CrisprCas12aMultiplexedSnpStudy).order_by(CrisprCas12aMultiplexedSnpStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
