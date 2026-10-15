"""Repository for Phase 542: Autonomous Direct RNA Nanopore Sequencing Pseudouridine (Ψ) Chemical Stoichiometry Profiler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.direct_rna_pseudouridine_nanopore_sequencing import (
    DirectRnaPseudouridineNanoporeSequencingStudy,
    DirectRnaPseudouridineNanoporeSequencingItemProfile,
    DirectRnaPseudouridineNanoporeSequencingMetricTrace,
)


class DirectRnaPseudouridineNanoporeSequencingRepository:
    """Database operations for Autonomous Direct RNA Nanopore Sequencing Pseudouridine (Ψ) Chemical Stoichiometry Profiler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Native Human rRNA and mRNA Direct Oxford Nanopore Sequencing with CMC Chemical Adduct Validation",
        analytical_modality: str = "direct-rna-pseudouridine-stoichiometry",
        pseudouridine_stoichiometry_detection_accuracy: float = 0.978,
        ionic_current_dwell_shift_sigma: float = 3.42,
        single_molecule_modification_calling_f1: float = 0.965,
        low_abundance_transcript_coverage_depth: float = 450.0,
        confidence_score: float = 0.995,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> DirectRnaPseudouridineNanoporeSequencingStudy:
        study = DirectRnaPseudouridineNanoporeSequencingStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            pseudouridine_stoichiometry_detection_accuracy=pseudouridine_stoichiometry_detection_accuracy,
            ionic_current_dwell_shift_sigma=ionic_current_dwell_shift_sigma,
            single_molecule_modification_calling_f1=single_molecule_modification_calling_f1,
            low_abundance_transcript_coverage_depth=low_abundance_transcript_coverage_depth,
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
    ) -> DirectRnaPseudouridineNanoporeSequencingItemProfile:
        item = DirectRnaPseudouridineNanoporeSequencingItemProfile(
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
    ) -> DirectRnaPseudouridineNanoporeSequencingMetricTrace:
        trace = DirectRnaPseudouridineNanoporeSequencingMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[DirectRnaPseudouridineNanoporeSequencingStudy]:
        stmt = (
            select(DirectRnaPseudouridineNanoporeSequencingStudy)
            .where(DirectRnaPseudouridineNanoporeSequencingStudy.id == study_id)
            .options(
                selectinload(DirectRnaPseudouridineNanoporeSequencingStudy.item_profiles),
                selectinload(DirectRnaPseudouridineNanoporeSequencingStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[DirectRnaPseudouridineNanoporeSequencingStudy]:
        stmt = (
            select(DirectRnaPseudouridineNanoporeSequencingStudy)
            .order_by(DirectRnaPseudouridineNanoporeSequencingStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(DirectRnaPseudouridineNanoporeSequencingStudy.item_profiles),
                selectinload(DirectRnaPseudouridineNanoporeSequencingStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
