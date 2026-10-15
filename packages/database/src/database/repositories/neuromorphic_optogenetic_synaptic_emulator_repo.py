"""Repository for Phase 543: Autonomous Biomimetic Neuromorphic Optoelectronic Synapse Photo-Memristive Plasticity Forecaster."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.neuromorphic_optogenetic_synaptic_emulator import (
    NeuromorphicOptogeneticSynapticEmulatorStudy,
    NeuromorphicOptogeneticSynapticEmulatorItemProfile,
    NeuromorphicOptogeneticSynapticEmulatorMetricTrace,
)


class NeuromorphicOptogeneticSynapticEmulatorRepository:
    """Database operations for Autonomous Biomimetic Neuromorphic Optoelectronic Synapse Photo-Memristive Plasticity Forecaster."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "2D Transition Metal Dichalcogenide (MoS2) / Perovskite Heterostructure Optoelectronic Synaptic Memristor",
        analytical_modality: str = "optoelectronic-synapse-plasticity",
        paired_pulse_facilitation_ppf_index_pct: float = 168.0,
        photo_induced_potentiation_energy_per_spike_fj: float = 45.0,
        non_volatile_memory_retention_days: float = 120.0,
        linear_weight_update_dynamic_range: float = 4.8,
        confidence_score: float = 0.994,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> NeuromorphicOptogeneticSynapticEmulatorStudy:
        study = NeuromorphicOptogeneticSynapticEmulatorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            paired_pulse_facilitation_ppf_index_pct=paired_pulse_facilitation_ppf_index_pct,
            photo_induced_potentiation_energy_per_spike_fj=photo_induced_potentiation_energy_per_spike_fj,
            non_volatile_memory_retention_days=non_volatile_memory_retention_days,
            linear_weight_update_dynamic_range=linear_weight_update_dynamic_range,
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
    ) -> NeuromorphicOptogeneticSynapticEmulatorItemProfile:
        item = NeuromorphicOptogeneticSynapticEmulatorItemProfile(
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
    ) -> NeuromorphicOptogeneticSynapticEmulatorMetricTrace:
        trace = NeuromorphicOptogeneticSynapticEmulatorMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[NeuromorphicOptogeneticSynapticEmulatorStudy]:
        stmt = (
            select(NeuromorphicOptogeneticSynapticEmulatorStudy)
            .where(NeuromorphicOptogeneticSynapticEmulatorStudy.id == study_id)
            .options(
                selectinload(NeuromorphicOptogeneticSynapticEmulatorStudy.item_profiles),
                selectinload(NeuromorphicOptogeneticSynapticEmulatorStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[NeuromorphicOptogeneticSynapticEmulatorStudy]:
        stmt = (
            select(NeuromorphicOptogeneticSynapticEmulatorStudy)
            .order_by(NeuromorphicOptogeneticSynapticEmulatorStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(NeuromorphicOptogeneticSynapticEmulatorStudy.item_profiles),
                selectinload(NeuromorphicOptogeneticSynapticEmulatorStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
