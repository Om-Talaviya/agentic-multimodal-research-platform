"""Repository for Phase 490: Autonomous High-Density CMOS Microelectrode Array Neuromorphic Axonal Conduction Velocity Mapper."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cmos_mea_axonal_conduction import (
    CmosMeaAxonalConductionStudy,
    CmosMeaAxonalConductionItemProfile,
    CmosMeaAxonalConductionMetricTrace,
)


class CmosMeaAxonalConductionRepository:
    """Database operations for Autonomous High-Density CMOS Microelectrode Array Neuromorphic Axonal Conduction Velocity Mapper."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Rat Cortical Primary Neurons Cultured over 26,400 Platinum Electrode CMOS Biocompatible Chip",
        analytical_modality: str = "cmos-mea-axonal-conduction",
        axonal_action_potential_conduction_velocity_m_per_s: float = 0.65,
        spike_signal_to_noise_ratio_snr: float = 18.2,
        synaptic_propagation_latency_ms: float = 1.85,
        functional_synaptic_connectivity_density: float = 0.925,
        confidence_score: float = 0.993,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CmosMeaAxonalConductionStudy:
        study = CmosMeaAxonalConductionStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            axonal_action_potential_conduction_velocity_m_per_s=axonal_action_potential_conduction_velocity_m_per_s,
            spike_signal_to_noise_ratio_snr=spike_signal_to_noise_ratio_snr,
            synaptic_propagation_latency_ms=synaptic_propagation_latency_ms,
            functional_synaptic_connectivity_density=functional_synaptic_connectivity_density,
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
    ) -> CmosMeaAxonalConductionItemProfile:
        item = CmosMeaAxonalConductionItemProfile(
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
    ) -> CmosMeaAxonalConductionMetricTrace:
        trace = CmosMeaAxonalConductionMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CmosMeaAxonalConductionStudy]:
        result = await self.session.execute(
            select(CmosMeaAxonalConductionStudy)
            .options(
                selectinload(CmosMeaAxonalConductionStudy.item_profiles),
                selectinload(CmosMeaAxonalConductionStudy.metric_traces),
            )
            .where(CmosMeaAxonalConductionStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[CmosMeaAxonalConductionStudy]:
        result = await self.session.execute(
            select(CmosMeaAxonalConductionStudy)
            .options(
                selectinload(CmosMeaAxonalConductionStudy.item_profiles),
                selectinload(CmosMeaAxonalConductionStudy.metric_traces),
            )
            .order_by(CmosMeaAxonalConductionStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
