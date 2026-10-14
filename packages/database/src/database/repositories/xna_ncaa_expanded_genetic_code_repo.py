"""Repository for Phase 498: Autonomous Xenobiotic Non-Canonical Amino Acid Expanded Genetic Code Ribosome Translator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.xna_ncaa_expanded_genetic_code import (
    XnaNcaaExpandedGeneticCodeStudy,
    XnaNcaaExpandedGeneticCodeItemProfile,
    XnaNcaaExpandedGeneticCodeMetricTrace,
)


class XnaNcaaExpandedGeneticCodeRepository:
    """Database operations for Autonomous Xenobiotic Non-Canonical Amino Acid Expanded Genetic Code Ribosome Translator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Orthogonal Methionyl-tRNA Synthetase / tRNA Pair in Recoded E. coli C321.deltaA with UAG Amber Suppression",
        analytical_modality: str = "expanded-genetic-code-translation",
        ncaa_incorporation_fidelity_pct: float = 99.1,
        amber_uag_suppression_efficiency: float = 0.895,
        orthogonal_synthetase_catalytic_kcat_over_km: float = 18500.0,
        recombinant_protein_expression_yield_mg_per_L: float = 42.5,
        confidence_score: float = 0.992,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> XnaNcaaExpandedGeneticCodeStudy:
        study = XnaNcaaExpandedGeneticCodeStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            ncaa_incorporation_fidelity_pct=ncaa_incorporation_fidelity_pct,
            amber_uag_suppression_efficiency=amber_uag_suppression_efficiency,
            orthogonal_synthetase_catalytic_kcat_over_km=orthogonal_synthetase_catalytic_kcat_over_km,
            recombinant_protein_expression_yield_mg_per_L=recombinant_protein_expression_yield_mg_per_L,
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
    ) -> XnaNcaaExpandedGeneticCodeItemProfile:
        item = XnaNcaaExpandedGeneticCodeItemProfile(
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
    ) -> XnaNcaaExpandedGeneticCodeMetricTrace:
        trace = XnaNcaaExpandedGeneticCodeMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[XnaNcaaExpandedGeneticCodeStudy]:
        result = await self.session.execute(
            select(XnaNcaaExpandedGeneticCodeStudy)
            .options(
                selectinload(XnaNcaaExpandedGeneticCodeStudy.item_profiles),
                selectinload(XnaNcaaExpandedGeneticCodeStudy.metric_traces),
            )
            .where(XnaNcaaExpandedGeneticCodeStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[XnaNcaaExpandedGeneticCodeStudy]:
        result = await self.session.execute(
            select(XnaNcaaExpandedGeneticCodeStudy)
            .options(
                selectinload(XnaNcaaExpandedGeneticCodeStudy.item_profiles),
                selectinload(XnaNcaaExpandedGeneticCodeStudy.metric_traces),
            )
            .order_by(XnaNcaaExpandedGeneticCodeStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
