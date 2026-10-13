"""Repository for Phase 448: Autonomous Synthetic Epigenetic Prime-Converter Base Insertion & Inverted Repeat Profiler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.synthetic_epigenetic_prime_converter import (
    SyntheticEpigeneticPrimeConverterStudy,
    SyntheticEpigeneticPrimeConverterItemProfile,
    SyntheticEpigeneticPrimeConverterMetricTrace,
)


class SyntheticEpigeneticPrimeConverterRepository:
    """Database operations for Autonomous Synthetic Epigenetic Prime-Converter Base Insertion & Inverted Repeat Profiler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Engineered PegRNA / Cas9-Nickase Prime Editor Complex on Methylated CpG Island",
        analytical_modality: str = "epigenetic-prime-conversion",
        peg_rna_extension_annealing_tm_celsius: float = 64.2,
        prime_conversion_efficiency_percentage: float = 78.5,
        cpg_demethylation_retention_ratio: float = 0.935,
        insertion_fidelity_indel_free_score: float = 0.982,
        confidence_score: float = 0.99,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SyntheticEpigeneticPrimeConverterStudy:
        study = SyntheticEpigeneticPrimeConverterStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            peg_rna_extension_annealing_tm_celsius=peg_rna_extension_annealing_tm_celsius,
            prime_conversion_efficiency_percentage=prime_conversion_efficiency_percentage,
            cpg_demethylation_retention_ratio=cpg_demethylation_retention_ratio,
            insertion_fidelity_indel_free_score=insertion_fidelity_indel_free_score,
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
    ) -> SyntheticEpigeneticPrimeConverterItemProfile:
        item = SyntheticEpigeneticPrimeConverterItemProfile(
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
    ) -> SyntheticEpigeneticPrimeConverterMetricTrace:
        trace = SyntheticEpigeneticPrimeConverterMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SyntheticEpigeneticPrimeConverterStudy]:
        result = await self.session.execute(
            select(SyntheticEpigeneticPrimeConverterStudy)
            .options(
                selectinload(SyntheticEpigeneticPrimeConverterStudy.item_profiles),
                selectinload(SyntheticEpigeneticPrimeConverterStudy.metric_traces),
            )
            .where(SyntheticEpigeneticPrimeConverterStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[SyntheticEpigeneticPrimeConverterStudy]:
        result = await self.session.execute(
            select(SyntheticEpigeneticPrimeConverterStudy)
            .options(
                selectinload(SyntheticEpigeneticPrimeConverterStudy.item_profiles),
                selectinload(SyntheticEpigeneticPrimeConverterStudy.metric_traces),
            )
            .order_by(SyntheticEpigeneticPrimeConverterStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
