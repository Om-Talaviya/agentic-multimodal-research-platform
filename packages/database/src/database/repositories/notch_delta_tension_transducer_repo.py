"""Repository for Phase 461: Autonomous Synthetic Morphogenetic Cell-Cell Contact Notch-Delta Mechanical Tension Transducer."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.notch_delta_tension_transducer import (
    NotchDeltaTensionTransducerStudy,
    NotchDeltaTensionTransducerItemProfile,
    NotchDeltaTensionTransducerMetricTrace,
)


class NotchDeltaTensionTransducerRepository:
    """Database operations for Autonomous Synthetic Morphogenetic Cell-Cell Contact Notch-Delta Mechanical Tension Transducer."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Synthetic SynNotch Engineered Fibroblast Dual-Lattice Cell Sorting Array",
        analytical_modality: str = "notch-delta-mechanotransduction",
        mechanical_pulling_force_pico_newtons: float = 12.8,
        s2_s3_cleavage_transcription_activation_ratio: float = 8.65,
        lateral_inhibition_bistability_index: float = 0.925,
        boundary_sharpening_transition_width_cell_diameters: float = 1.4,
        confidence_score: float = 0.991,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> NotchDeltaTensionTransducerStudy:
        study = NotchDeltaTensionTransducerStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            mechanical_pulling_force_pico_newtons=mechanical_pulling_force_pico_newtons,
            s2_s3_cleavage_transcription_activation_ratio=s2_s3_cleavage_transcription_activation_ratio,
            lateral_inhibition_bistability_index=lateral_inhibition_bistability_index,
            boundary_sharpening_transition_width_cell_diameters=boundary_sharpening_transition_width_cell_diameters,
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
    ) -> NotchDeltaTensionTransducerItemProfile:
        item = NotchDeltaTensionTransducerItemProfile(
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
    ) -> NotchDeltaTensionTransducerMetricTrace:
        trace = NotchDeltaTensionTransducerMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[NotchDeltaTensionTransducerStudy]:
        result = await self.session.execute(
            select(NotchDeltaTensionTransducerStudy)
            .options(
                selectinload(NotchDeltaTensionTransducerStudy.item_profiles),
                selectinload(NotchDeltaTensionTransducerStudy.metric_traces),
            )
            .where(NotchDeltaTensionTransducerStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[NotchDeltaTensionTransducerStudy]:
        result = await self.session.execute(
            select(NotchDeltaTensionTransducerStudy)
            .options(
                selectinload(NotchDeltaTensionTransducerStudy.item_profiles),
                selectinload(NotchDeltaTensionTransducerStudy.metric_traces),
            )
            .order_by(NotchDeltaTensionTransducerStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
