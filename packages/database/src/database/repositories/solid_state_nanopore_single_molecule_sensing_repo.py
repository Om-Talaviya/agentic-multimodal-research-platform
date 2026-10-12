"""Repository for Phase 417: Autonomous Solid-State Silicon Nitride Nanopore Single-Molecule Protein Translocation Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.solid_state_nanopore_single_molecule_sensing import (
    SolidStateNanoporeSensingStudy,
    SolidStateNanoporeSensingItemProfile,
    SolidStateNanoporeSensingMetricTrace,
)


class SolidStateNanoporeSensingRepository:
    """Database operations for Autonomous Solid-State Silicon Nitride Nanopore Single-Molecule Protein Translocation Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Conformationally Stretched Native Protein Translocation Through Sub-5nm SiNx Nanopore",
        analytical_modality: str = "solid-state-nanopore",
        translocation_dwell_time_us: float = 245.0,
        fractional_current_blockade_ratio: float = 0.785,
        nanopore_diameter_nm: float = 3.8,
        capture_frequency_events_per_s: float = 18.5,
        confidence_score: float = 0.988,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SolidStateNanoporeSensingStudy:
        study = SolidStateNanoporeSensingStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            translocation_dwell_time_us=translocation_dwell_time_us,
            fractional_current_blockade_ratio=fractional_current_blockade_ratio,
            nanopore_diameter_nm=nanopore_diameter_nm,
            capture_frequency_events_per_s=capture_frequency_events_per_s,
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
    ) -> SolidStateNanoporeSensingItemProfile:
        item = SolidStateNanoporeSensingItemProfile(
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
    ) -> SolidStateNanoporeSensingMetricTrace:
        trace = SolidStateNanoporeSensingMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SolidStateNanoporeSensingStudy]:
        result = await self.session.execute(
            select(SolidStateNanoporeSensingStudy)
            .options(
                selectinload(SolidStateNanoporeSensingStudy.item_profiles),
                selectinload(SolidStateNanoporeSensingStudy.metric_traces),
            )
            .where(SolidStateNanoporeSensingStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[SolidStateNanoporeSensingStudy]:
        result = await self.session.execute(
            select(SolidStateNanoporeSensingStudy)
            .options(
                selectinload(SolidStateNanoporeSensingStudy.item_profiles),
                selectinload(SolidStateNanoporeSensingStudy.metric_traces),
            )
            .order_by(SolidStateNanoporeSensingStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
