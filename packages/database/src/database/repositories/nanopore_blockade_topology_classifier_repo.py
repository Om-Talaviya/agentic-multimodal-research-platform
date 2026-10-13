"""Repository for Phase 450: Autonomous Nanopore Ionic Current Blockade Shape Classifier for Macromolecular Topologies."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.nanopore_blockade_topology_classifier import (
    NanoporeBlockadeTopologyStudy,
    NanoporeBlockadeTopologyItemProfile,
    NanoporeBlockadeTopologyMetricTrace,
)


class NanoporeBlockadeTopologyRepository:
    """Database operations for Autonomous Nanopore Ionic Current Blockade Shape Classifier for Macromolecular Topologies."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Supercoiled Plasmid DNA and Knotted Circular Peptides Passing Through 4nm Aerolysin Pore",
        analytical_modality: str = "nanopore-blockade-topology",
        dwell_time_topological_knot_us: float = 84.5,
        fractional_blockade_current_depth_ratio: float = 0.892,
        topology_classification_accuracy: float = 0.978,
        translocation_velocity_nt_per_ms: float = 4.2,
        confidence_score: float = 0.992,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> NanoporeBlockadeTopologyStudy:
        study = NanoporeBlockadeTopologyStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            dwell_time_topological_knot_us=dwell_time_topological_knot_us,
            fractional_blockade_current_depth_ratio=fractional_blockade_current_depth_ratio,
            topology_classification_accuracy=topology_classification_accuracy,
            translocation_velocity_nt_per_ms=translocation_velocity_nt_per_ms,
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
    ) -> NanoporeBlockadeTopologyItemProfile:
        item = NanoporeBlockadeTopologyItemProfile(
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
    ) -> NanoporeBlockadeTopologyMetricTrace:
        trace = NanoporeBlockadeTopologyMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[NanoporeBlockadeTopologyStudy]:
        result = await self.session.execute(
            select(NanoporeBlockadeTopologyStudy)
            .options(
                selectinload(NanoporeBlockadeTopologyStudy.item_profiles),
                selectinload(NanoporeBlockadeTopologyStudy.metric_traces),
            )
            .where(NanoporeBlockadeTopologyStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[NanoporeBlockadeTopologyStudy]:
        result = await self.session.execute(
            select(NanoporeBlockadeTopologyStudy)
            .options(
                selectinload(NanoporeBlockadeTopologyStudy.item_profiles),
                selectinload(NanoporeBlockadeTopologyStudy.metric_traces),
            )
            .order_by(NanoporeBlockadeTopologyStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
