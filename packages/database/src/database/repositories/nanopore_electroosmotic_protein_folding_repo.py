"""Repository for Phase 553: Autonomous Nanopore Electro-Osmotic Trap Protein Native State Unfolding & Refolding Kinetics Modeler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.nanopore_electroosmotic_protein_folding import (
    NanoporeElectroosmoticProteinFoldingStudy,
    NanoporeElectroosmoticProteinFoldingItemProfile,
    NanoporeElectroosmoticProteinFoldingMetricTrace,
)


class NanoporeElectroosmoticProteinFoldingRepository:
    """Database operations for Autonomous Nanopore Electro-Osmotic Trap Protein Native State Unfolding & Refolding Kinetics Modeler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Single Bovine Carbonic Anhydrase II trapped in ClyA Biological Nanopore under Variable Transmembrane Voltage Bias",
        analytical_modality: str = "nanopore-electroosmotic-folding",
        single_molecule_trap_dwell_time_s: float = 14.5,
        electroosmotic_holding_force_pn: float = 8.2,
        unfolding_activation_free_energy_barrier_kt: float = 18.6,
        refolding_transition_rate_per_second: float = 32.4,
        confidence_score: float = 0.995,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> NanoporeElectroosmoticProteinFoldingStudy:
        study = NanoporeElectroosmoticProteinFoldingStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            single_molecule_trap_dwell_time_s=single_molecule_trap_dwell_time_s,
            electroosmotic_holding_force_pn=electroosmotic_holding_force_pn,
            unfolding_activation_free_energy_barrier_kt=unfolding_activation_free_energy_barrier_kt,
            refolding_transition_rate_per_second=refolding_transition_rate_per_second,
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
    ) -> NanoporeElectroosmoticProteinFoldingItemProfile:
        item = NanoporeElectroosmoticProteinFoldingItemProfile(
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
    ) -> NanoporeElectroosmoticProteinFoldingMetricTrace:
        trace = NanoporeElectroosmoticProteinFoldingMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[NanoporeElectroosmoticProteinFoldingStudy]:
        stmt = (
            select(NanoporeElectroosmoticProteinFoldingStudy)
            .where(NanoporeElectroosmoticProteinFoldingStudy.id == study_id)
            .options(
                selectinload(NanoporeElectroosmoticProteinFoldingStudy.item_profiles),
                selectinload(NanoporeElectroosmoticProteinFoldingStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[NanoporeElectroosmoticProteinFoldingStudy]:
        stmt = (
            select(NanoporeElectroosmoticProteinFoldingStudy)
            .order_by(NanoporeElectroosmoticProteinFoldingStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(NanoporeElectroosmoticProteinFoldingStudy.item_profiles),
                selectinload(NanoporeElectroosmoticProteinFoldingStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
