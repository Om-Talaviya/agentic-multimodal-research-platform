"""Repository for Phase 525: Autonomous Engineered Cas12a Direct RNA Single-Nucleotide Variant Diagnostic Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.crispr_cas12a_direct_rna_targeting_diagnostics import (
    CrisprCas12aDirectRnaTargetingDiagnosticsStudy,
    CrisprCas12aDirectRnaTargetingDiagnosticsItemProfile,
    CrisprCas12aDirectRnaTargetingDiagnosticsMetricTrace,
)


class CrisprCas12aDirectRnaTargetingDiagnosticsRepository:
    """Database operations for Autonomous Engineered Cas12a Direct RNA Single-Nucleotide Variant Diagnostic Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Engineered Dual-Domain Acidaminococcus sp. Cas12a Variant bound to Synthetic SARS-CoV-3 RNA Target",
        analytical_modality: str = "cas12a-direct-rna-cleavage",
        collateral_ssdna_probe_turnover_rate_s_inv: float = 240.0,
        single_nucleotide_variant_specificity_ratio: float = 85.0,
        limit_of_detection_attomolar_aM: float = 15.0,
        isothermal_reaction_kinetic_delay_time_min: float = 12.0,
        confidence_score: float = 0.996,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CrisprCas12aDirectRnaTargetingDiagnosticsStudy:
        study = CrisprCas12aDirectRnaTargetingDiagnosticsStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            collateral_ssdna_probe_turnover_rate_s_inv=collateral_ssdna_probe_turnover_rate_s_inv,
            single_nucleotide_variant_specificity_ratio=single_nucleotide_variant_specificity_ratio,
            limit_of_detection_attomolar_aM=limit_of_detection_attomolar_aM,
            isothermal_reaction_kinetic_delay_time_min=isothermal_reaction_kinetic_delay_time_min,
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
    ) -> CrisprCas12aDirectRnaTargetingDiagnosticsItemProfile:
        item = CrisprCas12aDirectRnaTargetingDiagnosticsItemProfile(
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
    ) -> CrisprCas12aDirectRnaTargetingDiagnosticsMetricTrace:
        trace = CrisprCas12aDirectRnaTargetingDiagnosticsMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CrisprCas12aDirectRnaTargetingDiagnosticsStudy]:
        result = await self.session.execute(
            select(CrisprCas12aDirectRnaTargetingDiagnosticsStudy)
            .options(
                selectinload(CrisprCas12aDirectRnaTargetingDiagnosticsStudy.item_profiles),
                selectinload(CrisprCas12aDirectRnaTargetingDiagnosticsStudy.metric_traces),
            )
            .where(CrisprCas12aDirectRnaTargetingDiagnosticsStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[CrisprCas12aDirectRnaTargetingDiagnosticsStudy]:
        result = await self.session.execute(
            select(CrisprCas12aDirectRnaTargetingDiagnosticsStudy)
            .options(
                selectinload(CrisprCas12aDirectRnaTargetingDiagnosticsStudy.item_profiles),
                selectinload(CrisprCas12aDirectRnaTargetingDiagnosticsStudy.metric_traces),
            )
            .order_by(CrisprCas12aDirectRnaTargetingDiagnosticsStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
