"""Repository for Phase 517: Autonomous Dual-Color Multiplexed Optogenetic Neocortical Oscillatory Synchrony Mapper."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.multiplexed_optogenetic_neocortical_synchrony import (
    MultiplexedOptogeneticNeocorticalSynchronyStudy,
    MultiplexedOptogeneticNeocorticalSynchronyItemProfile,
    MultiplexedOptogeneticNeocorticalSynchronyMetricTrace,
)


class MultiplexedOptogeneticNeocorticalSynchronyRepository:
    """Database operations for Autonomous Dual-Color Multiplexed Optogenetic Neocortical Oscillatory Synchrony Mapper."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Transgenic Mouse Somatosensory Cortex expressing ChRmine (Red) and ChETA (Blue) in Layer 2/3 and 5",
        analytical_modality: str = "dual-color-optogenetic-synchrony",
        gamma_band_phase_locking_value_plv: float = 0.895,
        optical_crosstalk_attenuation_ratio: float = 42.0,
        spike_timing_jitter_precision_std_ms: float = 0.45,
        cross_layer_laminar_information_transfer_entropy: float = 0.68,
        confidence_score: float = 0.993,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MultiplexedOptogeneticNeocorticalSynchronyStudy:
        study = MultiplexedOptogeneticNeocorticalSynchronyStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            gamma_band_phase_locking_value_plv=gamma_band_phase_locking_value_plv,
            optical_crosstalk_attenuation_ratio=optical_crosstalk_attenuation_ratio,
            spike_timing_jitter_precision_std_ms=spike_timing_jitter_precision_std_ms,
            cross_layer_laminar_information_transfer_entropy=cross_layer_laminar_information_transfer_entropy,
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
    ) -> MultiplexedOptogeneticNeocorticalSynchronyItemProfile:
        item = MultiplexedOptogeneticNeocorticalSynchronyItemProfile(
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
    ) -> MultiplexedOptogeneticNeocorticalSynchronyMetricTrace:
        trace = MultiplexedOptogeneticNeocorticalSynchronyMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MultiplexedOptogeneticNeocorticalSynchronyStudy]:
        result = await self.session.execute(
            select(MultiplexedOptogeneticNeocorticalSynchronyStudy)
            .options(
                selectinload(MultiplexedOptogeneticNeocorticalSynchronyStudy.item_profiles),
                selectinload(MultiplexedOptogeneticNeocorticalSynchronyStudy.metric_traces),
            )
            .where(MultiplexedOptogeneticNeocorticalSynchronyStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[MultiplexedOptogeneticNeocorticalSynchronyStudy]:
        result = await self.session.execute(
            select(MultiplexedOptogeneticNeocorticalSynchronyStudy)
            .options(
                selectinload(MultiplexedOptogeneticNeocorticalSynchronyStudy.item_profiles),
                selectinload(MultiplexedOptogeneticNeocorticalSynchronyStudy.metric_traces),
            )
            .order_by(MultiplexedOptogeneticNeocorticalSynchronyStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
