"""Repository for Phase 562: Autonomous Synthetic Xenobiotic Unnatural Base Pair (UBP: dNaM-d5SICS) DNA Replication Fidelity Forecaster."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.synthetic_xenobiotic_ubp_replication_fidelity import (
    SyntheticXenobioticUbpReplicationFidelityStudy,
    SyntheticXenobioticUbpReplicationFidelityItemProfile,
    SyntheticXenobioticUbpReplicationFidelityMetricTrace,
)


class SyntheticXenobioticUbpReplicationFidelityRepository:
    """Database operations for Autonomous Synthetic Xenobiotic Unnatural Base Pair (UBP: dNaM-d5SICS) DNA Replication Fidelity Forecaster."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Engineered Semi-Synthetic Organism E. coli with dNaM-d5SICS 6-Letter Genetic Alphabet and Nucleoside Triphosphate Transporter",
        analytical_modality: str = "xenobiotic-unnatural-base-pair",
        six_letter_replication_fidelity_pct_per_doubling: float = 99.82,
        ubp_retention_half_life_generations: float = 145.0,
        unnatural_triphosphate_uptake_flux_pmol_min: float = 28.4,
        polymerase_bypass_insertion_efficiency_kcat_km: float = 480000.0,
        confidence_score: float = 0.996,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SyntheticXenobioticUbpReplicationFidelityStudy:
        study = SyntheticXenobioticUbpReplicationFidelityStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            six_letter_replication_fidelity_pct_per_doubling=six_letter_replication_fidelity_pct_per_doubling,
            ubp_retention_half_life_generations=ubp_retention_half_life_generations,
            unnatural_triphosphate_uptake_flux_pmol_min=unnatural_triphosphate_uptake_flux_pmol_min,
            polymerase_bypass_insertion_efficiency_kcat_km=polymerase_bypass_insertion_efficiency_kcat_km,
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
    ) -> SyntheticXenobioticUbpReplicationFidelityItemProfile:
        item = SyntheticXenobioticUbpReplicationFidelityItemProfile(
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
    ) -> SyntheticXenobioticUbpReplicationFidelityMetricTrace:
        trace = SyntheticXenobioticUbpReplicationFidelityMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SyntheticXenobioticUbpReplicationFidelityStudy]:
        stmt = (
            select(SyntheticXenobioticUbpReplicationFidelityStudy)
            .where(SyntheticXenobioticUbpReplicationFidelityStudy.id == study_id)
            .options(
                selectinload(SyntheticXenobioticUbpReplicationFidelityStudy.item_profiles),
                selectinload(SyntheticXenobioticUbpReplicationFidelityStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[SyntheticXenobioticUbpReplicationFidelityStudy]:
        stmt = (
            select(SyntheticXenobioticUbpReplicationFidelityStudy)
            .order_by(SyntheticXenobioticUbpReplicationFidelityStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(SyntheticXenobioticUbpReplicationFidelityStudy.item_profiles),
                selectinload(SyntheticXenobioticUbpReplicationFidelityStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
