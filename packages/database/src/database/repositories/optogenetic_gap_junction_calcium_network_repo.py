"""Repository for Phase 554: Autonomous Optogenetic Intercellular Gap Junction Coupling & Calcium Synchrony Network Forecaster."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.optogenetic_gap_junction_calcium_network import (
    OptogeneticGapJunctionCalciumNetworkStudy,
    OptogeneticGapJunctionCalciumNetworkItemProfile,
    OptogeneticGapJunctionCalciumNetworkMetricTrace,
)


class OptogeneticGapJunctionCalciumNetworkRepository:
    """Database operations for Autonomous Optogenetic Intercellular Gap Junction Coupling & Calcium Synchrony Network Forecaster."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Confluent Monolayer of Human Induced Pluripotent Stem Cell-Derived Cardiomyocytes expressing Channelrhodopsin-2 and Connexin-43",
        analytical_modality: str = "optogenetic-gap-junction-sync",
        calcium_wave_propagation_velocity_um_s: float = 380.0,
        connexin43_gap_junction_conductance_ns: float = 42.5,
        network_phase_synchronization_order_param: float = 0.965,
        action_potential_duration_apd90_ms: float = 310.0,
        confidence_score: float = 0.996,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> OptogeneticGapJunctionCalciumNetworkStudy:
        study = OptogeneticGapJunctionCalciumNetworkStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            calcium_wave_propagation_velocity_um_s=calcium_wave_propagation_velocity_um_s,
            connexin43_gap_junction_conductance_ns=connexin43_gap_junction_conductance_ns,
            network_phase_synchronization_order_param=network_phase_synchronization_order_param,
            action_potential_duration_apd90_ms=action_potential_duration_apd90_ms,
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
    ) -> OptogeneticGapJunctionCalciumNetworkItemProfile:
        item = OptogeneticGapJunctionCalciumNetworkItemProfile(
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
    ) -> OptogeneticGapJunctionCalciumNetworkMetricTrace:
        trace = OptogeneticGapJunctionCalciumNetworkMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[OptogeneticGapJunctionCalciumNetworkStudy]:
        stmt = (
            select(OptogeneticGapJunctionCalciumNetworkStudy)
            .where(OptogeneticGapJunctionCalciumNetworkStudy.id == study_id)
            .options(
                selectinload(OptogeneticGapJunctionCalciumNetworkStudy.item_profiles),
                selectinload(OptogeneticGapJunctionCalciumNetworkStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[OptogeneticGapJunctionCalciumNetworkStudy]:
        stmt = (
            select(OptogeneticGapJunctionCalciumNetworkStudy)
            .order_by(OptogeneticGapJunctionCalciumNetworkStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(OptogeneticGapJunctionCalciumNetworkStudy.item_profiles),
                selectinload(OptogeneticGapJunctionCalciumNetworkStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
