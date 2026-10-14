"""Repository for Phase 521: Autonomous Biomolecular Protein Nanofiber Memristive Synaptic Weight Plasticity Forecaster."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.neuromorphic_memristive_synapse_protein import (
    NeuromorphicMemristiveSynapseProteinStudy,
    NeuromorphicMemristiveSynapseProteinItemProfile,
    NeuromorphicMemristiveSynapseProteinMetricTrace,
)


class NeuromorphicMemristiveSynapseProteinRepository:
    """Database operations for Autonomous Biomolecular Protein Nanofiber Memristive Synaptic Weight Plasticity Forecaster."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Crossbar Array of Self-Assembled Amyloid-beta / Ferritin Bio-Nanowires sandwiched between Pt/Au Electrodes",
        analytical_modality: str = "biomolecular-memristor-plasticity",
        conductance_switching_on_off_ratio: float = 185.0,
        spike_timing_dependent_plasticity_stdp_tau_ms: float = 24.5,
        analog_conductance_states_count: float = 64.0,
        endurance_switching_cycles: float = 50000.0,
        confidence_score: float = 0.992,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> NeuromorphicMemristiveSynapseProteinStudy:
        study = NeuromorphicMemristiveSynapseProteinStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            conductance_switching_on_off_ratio=conductance_switching_on_off_ratio,
            spike_timing_dependent_plasticity_stdp_tau_ms=spike_timing_dependent_plasticity_stdp_tau_ms,
            analog_conductance_states_count=analog_conductance_states_count,
            endurance_switching_cycles=endurance_switching_cycles,
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
    ) -> NeuromorphicMemristiveSynapseProteinItemProfile:
        item = NeuromorphicMemristiveSynapseProteinItemProfile(
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
    ) -> NeuromorphicMemristiveSynapseProteinMetricTrace:
        trace = NeuromorphicMemristiveSynapseProteinMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[NeuromorphicMemristiveSynapseProteinStudy]:
        result = await self.session.execute(
            select(NeuromorphicMemristiveSynapseProteinStudy)
            .options(
                selectinload(NeuromorphicMemristiveSynapseProteinStudy.item_profiles),
                selectinload(NeuromorphicMemristiveSynapseProteinStudy.metric_traces),
            )
            .where(NeuromorphicMemristiveSynapseProteinStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[NeuromorphicMemristiveSynapseProteinStudy]:
        result = await self.session.execute(
            select(NeuromorphicMemristiveSynapseProteinStudy)
            .options(
                selectinload(NeuromorphicMemristiveSynapseProteinStudy.item_profiles),
                selectinload(NeuromorphicMemristiveSynapseProteinStudy.metric_traces),
            )
            .order_by(NeuromorphicMemristiveSynapseProteinStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
