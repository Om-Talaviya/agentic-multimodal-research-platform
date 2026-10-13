"""Repository for Phase 453: Autonomous Quantum Dots-Mediated Optoelectronic Neuromorphic Synaptic Potentiation Modeler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.quantum_dots_optoelectronic_synapse import (
    QuantumDotsOptoelectronicSynapseStudy,
    QuantumDotsOptoelectronicSynapseItemProfile,
    QuantumDotsOptoelectronicSynapseMetricTrace,
)


class QuantumDotsOptoelectronicSynapseRepository:
    """Database operations for Autonomous Quantum Dots-Mediated Optoelectronic Neuromorphic Synaptic Potentiation Modeler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "InP/ZnS Core-Shell Quantum Dot Photo-Memristor Synapse Coupled to Primary Cortical Neurons",
        analytical_modality: str = "qd-optoelectronic-synapse",
        paired_pulse_facilitation_ppf_ratio: float = 1.82,
        photocurrent_relaxation_lifetime_ms: float = 245.0,
        synaptic_weight_plasticity_dynamic_range: float = 4.65,
        energy_consumption_per_spike_femtojoules: float = 82.0,
        confidence_score: float = 0.991,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> QuantumDotsOptoelectronicSynapseStudy:
        study = QuantumDotsOptoelectronicSynapseStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            paired_pulse_facilitation_ppf_ratio=paired_pulse_facilitation_ppf_ratio,
            photocurrent_relaxation_lifetime_ms=photocurrent_relaxation_lifetime_ms,
            synaptic_weight_plasticity_dynamic_range=synaptic_weight_plasticity_dynamic_range,
            energy_consumption_per_spike_femtojoules=energy_consumption_per_spike_femtojoules,
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
    ) -> QuantumDotsOptoelectronicSynapseItemProfile:
        item = QuantumDotsOptoelectronicSynapseItemProfile(
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
    ) -> QuantumDotsOptoelectronicSynapseMetricTrace:
        trace = QuantumDotsOptoelectronicSynapseMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[QuantumDotsOptoelectronicSynapseStudy]:
        result = await self.session.execute(
            select(QuantumDotsOptoelectronicSynapseStudy)
            .options(
                selectinload(QuantumDotsOptoelectronicSynapseStudy.item_profiles),
                selectinload(QuantumDotsOptoelectronicSynapseStudy.metric_traces),
            )
            .where(QuantumDotsOptoelectronicSynapseStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[QuantumDotsOptoelectronicSynapseStudy]:
        result = await self.session.execute(
            select(QuantumDotsOptoelectronicSynapseStudy)
            .options(
                selectinload(QuantumDotsOptoelectronicSynapseStudy.item_profiles),
                selectinload(QuantumDotsOptoelectronicSynapseStudy.metric_traces),
            )
            .order_by(QuantumDotsOptoelectronicSynapseStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
