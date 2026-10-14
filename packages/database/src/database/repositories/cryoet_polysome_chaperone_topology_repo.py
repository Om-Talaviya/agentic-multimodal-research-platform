"""Repository for Phase 481: Autonomous In-Situ Cryo-ET Ribosome Polysome Structural Topology & Nascent Chain Chaperone Coordinator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cryoet_polysome_chaperone_topology import (
    CryoetPolysomeChaperoneTopologyStudy,
    CryoetPolysomeChaperoneTopologyItemProfile,
    CryoetPolysomeChaperoneTopologyMetricTrace,
)


class CryoetPolysomeChaperoneTopologyRepository:
    """Database operations for Autonomous In-Situ Cryo-ET Ribosome Polysome Structural Topology & Nascent Chain Chaperone Coordinator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Vitrified Mammalian Reticulocyte Cytoplasm with Circular Polysome-Hsp70 Chaperone Ensembles",
        analytical_modality: str = "cryoet-polysome-topology",
        inter_ribosomal_exit_channel_distance_nm: float = 16.8,
        polysome_circularity_topology_index: float = 0.885,
        chaperone_nascent_chain_occupancy_ratio: float = 0.912,
        subtomogram_averaging_resolution_angstrom: float = 5.25,
        confidence_score: float = 0.993,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CryoetPolysomeChaperoneTopologyStudy:
        study = CryoetPolysomeChaperoneTopologyStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            inter_ribosomal_exit_channel_distance_nm=inter_ribosomal_exit_channel_distance_nm,
            polysome_circularity_topology_index=polysome_circularity_topology_index,
            chaperone_nascent_chain_occupancy_ratio=chaperone_nascent_chain_occupancy_ratio,
            subtomogram_averaging_resolution_angstrom=subtomogram_averaging_resolution_angstrom,
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
    ) -> CryoetPolysomeChaperoneTopologyItemProfile:
        item = CryoetPolysomeChaperoneTopologyItemProfile(
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
    ) -> CryoetPolysomeChaperoneTopologyMetricTrace:
        trace = CryoetPolysomeChaperoneTopologyMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CryoetPolysomeChaperoneTopologyStudy]:
        result = await self.session.execute(
            select(CryoetPolysomeChaperoneTopologyStudy)
            .options(
                selectinload(CryoetPolysomeChaperoneTopologyStudy.item_profiles),
                selectinload(CryoetPolysomeChaperoneTopologyStudy.metric_traces),
            )
            .where(CryoetPolysomeChaperoneTopologyStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[CryoetPolysomeChaperoneTopologyStudy]:
        result = await self.session.execute(
            select(CryoetPolysomeChaperoneTopologyStudy)
            .options(
                selectinload(CryoetPolysomeChaperoneTopologyStudy.item_profiles),
                selectinload(CryoetPolysomeChaperoneTopologyStudy.metric_traces),
            )
            .order_by(CryoetPolysomeChaperoneTopologyStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
