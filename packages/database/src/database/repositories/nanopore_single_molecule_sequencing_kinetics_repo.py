"""Repository for Phase 526: Autonomous Solid-State Nanopore Polymerase-Guided DNA Sequencing Kinetics Forecaster."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.nanopore_single_molecule_sequencing_kinetics import (
    NanoporeSingleMoleculeSequencingKineticsStudy,
    NanoporeSingleMoleculeSequencingKineticsItemProfile,
    NanoporeSingleMoleculeSequencingKineticsMetricTrace,
)


class NanoporeSingleMoleculeSequencingKineticsRepository:
    """Database operations for Autonomous Solid-State Nanopore Polymerase-Guided DNA Sequencing Kinetics Forecaster."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Phi29 DNA Polymerase Coupled to Sub-2nm Si3N4 Solid-State Nanopore with Fluorescent dNTP Analogues",
        analytical_modality: str = "nanopore-sequencing-kinetics",
        nucleotide_incorporation_dwell_time_ms: float = 18.5,
        polymerase_processivity_base_pairs: float = 2850.0,
        ionic_current_blockade_ratio: float = 0.76,
        sequencing_raw_error_rate_pct: float = 1.42,
        confidence_score: float = 0.995,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> NanoporeSingleMoleculeSequencingKineticsStudy:
        study = NanoporeSingleMoleculeSequencingKineticsStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            nucleotide_incorporation_dwell_time_ms=nucleotide_incorporation_dwell_time_ms,
            polymerase_processivity_base_pairs=polymerase_processivity_base_pairs,
            ionic_current_blockade_ratio=ionic_current_blockade_ratio,
            sequencing_raw_error_rate_pct=sequencing_raw_error_rate_pct,
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
    ) -> NanoporeSingleMoleculeSequencingKineticsItemProfile:
        item = NanoporeSingleMoleculeSequencingKineticsItemProfile(
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
    ) -> NanoporeSingleMoleculeSequencingKineticsMetricTrace:
        trace = NanoporeSingleMoleculeSequencingKineticsMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[NanoporeSingleMoleculeSequencingKineticsStudy]:
        stmt = (
            select(NanoporeSingleMoleculeSequencingKineticsStudy)
            .where(NanoporeSingleMoleculeSequencingKineticsStudy.id == study_id)
            .options(
                selectinload(NanoporeSingleMoleculeSequencingKineticsStudy.item_profiles),
                selectinload(NanoporeSingleMoleculeSequencingKineticsStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[NanoporeSingleMoleculeSequencingKineticsStudy]:
        stmt = (
            select(NanoporeSingleMoleculeSequencingKineticsStudy)
            .order_by(NanoporeSingleMoleculeSequencingKineticsStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(NanoporeSingleMoleculeSequencingKineticsStudy.item_profiles),
                selectinload(NanoporeSingleMoleculeSequencingKineticsStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
