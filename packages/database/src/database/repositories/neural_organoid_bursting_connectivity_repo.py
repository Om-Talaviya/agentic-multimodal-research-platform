"""Repository for Phase 463: Autonomous Neural Organoid Spontaneous Synchronous Bursting & Functional Connectivity Grapher."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.neural_organoid_bursting_connectivity import (
    NeuralOrganoidBurstingConnectivityStudy,
    NeuralOrganoidBurstingConnectivityItemProfile,
    NeuralOrganoidBurstingConnectivityMetricTrace,
)


class NeuralOrganoidBurstingConnectivityRepository:
    """Database operations for Autonomous Neural Organoid Spontaneous Synchronous Bursting & Functional Connectivity Grapher."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "6-Month Human Cerebral Cortical Organoid on 4096-Channel CMOS High-Density MEA",
        analytical_modality: str = "organoid-neural-connectivity",
        synchronous_network_burst_rate_hz: float = 0.35,
        graph_small_world_clustering_coefficient: float = 0.785,
        cross_correlation_functional_connectivity_density: float = 0.842,
        shannon_entropy_burst_complexity: float = 3.42,
        confidence_score: float = 0.992,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> NeuralOrganoidBurstingConnectivityStudy:
        study = NeuralOrganoidBurstingConnectivityStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            synchronous_network_burst_rate_hz=synchronous_network_burst_rate_hz,
            graph_small_world_clustering_coefficient=graph_small_world_clustering_coefficient,
            cross_correlation_functional_connectivity_density=cross_correlation_functional_connectivity_density,
            shannon_entropy_burst_complexity=shannon_entropy_burst_complexity,
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
    ) -> NeuralOrganoidBurstingConnectivityItemProfile:
        item = NeuralOrganoidBurstingConnectivityItemProfile(
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
    ) -> NeuralOrganoidBurstingConnectivityMetricTrace:
        trace = NeuralOrganoidBurstingConnectivityMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[NeuralOrganoidBurstingConnectivityStudy]:
        result = await self.session.execute(
            select(NeuralOrganoidBurstingConnectivityStudy)
            .options(
                selectinload(NeuralOrganoidBurstingConnectivityStudy.item_profiles),
                selectinload(NeuralOrganoidBurstingConnectivityStudy.metric_traces),
            )
            .where(NeuralOrganoidBurstingConnectivityStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[NeuralOrganoidBurstingConnectivityStudy]:
        result = await self.session.execute(
            select(NeuralOrganoidBurstingConnectivityStudy)
            .options(
                selectinload(NeuralOrganoidBurstingConnectivityStudy.item_profiles),
                selectinload(NeuralOrganoidBurstingConnectivityStudy.metric_traces),
            )
            .order_by(NeuralOrganoidBurstingConnectivityStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
