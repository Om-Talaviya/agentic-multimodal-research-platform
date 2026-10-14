"""Repository for Phase 508: Autonomous Solid-State Nanopore Single-Molecule Protein Co-Translocational Unfolding Modeler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.solid_state_nanopore_protein_unfolding import (
    SolidStateNanoporeProteinUnfoldingStudy,
    SolidStateNanoporeProteinUnfoldingItemProfile,
    SolidStateNanoporeProteinUnfoldingMetricTrace,
)


class SolidStateNanoporeProteinUnfoldingRepository:
    """Database operations for Autonomous Solid-State Nanopore Single-Molecule Protein Co-Translocational Unfolding Modeler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Sub-3nm Low-Noise HfO2 Nanopore with ClpX-Coupled Maltose-Binding Protein Translocation",
        analytical_modality: str = "nanopore-protein-unfolding",
        unfolding_energy_barrier_height_kbT: float = 24.5,
        translocation_dwell_time_per_domain_ms: float = 8.2,
        residual_current_fraction_blockade: float = 0.765,
        single_amino_acid_substitutional_snr: float = 16.5,
        confidence_score: float = 0.993,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SolidStateNanoporeProteinUnfoldingStudy:
        study = SolidStateNanoporeProteinUnfoldingStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            unfolding_energy_barrier_height_kbT=unfolding_energy_barrier_height_kbT,
            translocation_dwell_time_per_domain_ms=translocation_dwell_time_per_domain_ms,
            residual_current_fraction_blockade=residual_current_fraction_blockade,
            single_amino_acid_substitutional_snr=single_amino_acid_substitutional_snr,
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
    ) -> SolidStateNanoporeProteinUnfoldingItemProfile:
        item = SolidStateNanoporeProteinUnfoldingItemProfile(
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
    ) -> SolidStateNanoporeProteinUnfoldingMetricTrace:
        trace = SolidStateNanoporeProteinUnfoldingMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SolidStateNanoporeProteinUnfoldingStudy]:
        result = await self.session.execute(
            select(SolidStateNanoporeProteinUnfoldingStudy)
            .options(
                selectinload(SolidStateNanoporeProteinUnfoldingStudy.item_profiles),
                selectinload(SolidStateNanoporeProteinUnfoldingStudy.metric_traces),
            )
            .where(SolidStateNanoporeProteinUnfoldingStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[SolidStateNanoporeProteinUnfoldingStudy]:
        result = await self.session.execute(
            select(SolidStateNanoporeProteinUnfoldingStudy)
            .options(
                selectinload(SolidStateNanoporeProteinUnfoldingStudy.item_profiles),
                selectinload(SolidStateNanoporeProteinUnfoldingStudy.metric_traces),
            )
            .order_by(SolidStateNanoporeProteinUnfoldingStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
