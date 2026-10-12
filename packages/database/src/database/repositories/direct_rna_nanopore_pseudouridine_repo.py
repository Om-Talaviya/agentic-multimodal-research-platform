"""Repository for Phase 415: Autonomous Epitranscriptomic Direct RNA Nanopore Pseudouridine (Psi) & m6A Stoichiometry Profiler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.direct_rna_nanopore_pseudouridine import (
    DirectRnaNanoporePseudouridineStudy,
    DirectRnaNanoporePseudouridineItemProfile,
    DirectRnaNanoporePseudouridineMetricTrace,
)


class DirectRnaNanoporePseudouridineRepository:
    """Database operations for Autonomous Epitranscriptomic Direct RNA Nanopore Pseudouridine (Psi) & m6A Stoichiometry Profiler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Cellular Poly(A)+ Native mRNA Transcriptome",
        analytical_modality: str = "direct-rna-nanopore",
        pseudouridine_stoichiometry_ratio: float = 0.842,
        nanopore_dwell_time_shift_ms: float = 14.8,
        ionic_current_deviation_pA: float = 6.2,
        m6a_modification_frequency: float = 0.765,
        confidence_score: float = 0.987,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> DirectRnaNanoporePseudouridineStudy:
        study = DirectRnaNanoporePseudouridineStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            pseudouridine_stoichiometry_ratio=pseudouridine_stoichiometry_ratio,
            nanopore_dwell_time_shift_ms=nanopore_dwell_time_shift_ms,
            ionic_current_deviation_pA=ionic_current_deviation_pA,
            m6a_modification_frequency=m6a_modification_frequency,
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
    ) -> DirectRnaNanoporePseudouridineItemProfile:
        item = DirectRnaNanoporePseudouridineItemProfile(
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
    ) -> DirectRnaNanoporePseudouridineMetricTrace:
        trace = DirectRnaNanoporePseudouridineMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[DirectRnaNanoporePseudouridineStudy]:
        result = await self.session.execute(
            select(DirectRnaNanoporePseudouridineStudy)
            .options(
                selectinload(DirectRnaNanoporePseudouridineStudy.item_profiles),
                selectinload(DirectRnaNanoporePseudouridineStudy.metric_traces),
            )
            .where(DirectRnaNanoporePseudouridineStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DirectRnaNanoporePseudouridineStudy]:
        result = await self.session.execute(
            select(DirectRnaNanoporePseudouridineStudy)
            .options(
                selectinload(DirectRnaNanoporePseudouridineStudy.item_profiles),
                selectinload(DirectRnaNanoporePseudouridineStudy.metric_traces),
            )
            .order_by(DirectRnaNanoporePseudouridineStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
