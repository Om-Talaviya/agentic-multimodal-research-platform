"""Repository for Phase 576: Autonomous Single-Molecule smFRET High-Fidelity DNA Polymerase Mismatch Proofreading & Exonuclease Kinetic Tracker."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.single_molecule_fret_polymerase_fidelity_tracker import (
    SingleMoleculeFretPolymeraseFidelityTrackerStudy,
    SingleMoleculeFretPolymeraseFidelityTrackerItemProfile,
    SingleMoleculeFretPolymeraseFidelityTrackerMetricTrace,
)


class SingleMoleculeFretPolymeraseFidelityTrackerRepository:
    """Repository for Autonomous Single-Molecule smFRET High-Fidelity DNA Polymerase Mismatch Proofreading & Exonuclease Kinetic Tracker storage and retrieval."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str,
        analytical_modality: str,
        fret_efficiency_transition_delta: float,
        exonuclease_proofreading_dwell_time_ms: float,
        mismatch_discrimination_factor: float,
        polymerization_catalytic_rate_nt_s: float,
        confidence_score: float = 0.997,
        status: str = "completed",
        summary_report: Optional[str] = None,
        parameters: Optional[dict] = None,
    ) -> SingleMoleculeFretPolymeraseFidelityTrackerStudy:
        study = SingleMoleculeFretPolymeraseFidelityTrackerStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            fret_efficiency_transition_delta=fret_efficiency_transition_delta,
            exonuclease_proofreading_dwell_time_ms=exonuclease_proofreading_dwell_time_ms,
            mismatch_discrimination_factor=mismatch_discrimination_factor,
            polymerization_catalytic_rate_nt_s=polymerization_catalytic_rate_nt_s,
            confidence_score=confidence_score,
            status=status,
            summary_report=summary_report,
            parameters=parameters or {},
        )
        self.session.add(study)
        await self.session.commit()
        await self.session.refresh(study)
        return study

    async def get_study(self, study_id: UUID) -> Optional[SingleMoleculeFretPolymeraseFidelityTrackerStudy]:
        stmt = select(SingleMoleculeFretPolymeraseFidelityTrackerStudy).where(SingleMoleculeFretPolymeraseFidelityTrackerStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[SingleMoleculeFretPolymeraseFidelityTrackerStudy]:
        stmt = select(SingleMoleculeFretPolymeraseFidelityTrackerStudy).order_by(SingleMoleculeFretPolymeraseFidelityTrackerStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_item_profile(
        self,
        study_id: UUID,
        item_name: str,
        quantitative_value: float,
        profile_category: str = "Analysis Profile",
        log2_fold_change: float = 1.5,
        significance_score: float = 0.95,
    ) -> SingleMoleculeFretPolymeraseFidelityTrackerItemProfile:
        profile = SingleMoleculeFretPolymeraseFidelityTrackerItemProfile(
            study_id=study_id,
            item_name=item_name,
            profile_category=profile_category,
            quantitative_value=quantitative_value,
            log2_fold_change=log2_fold_change,
            significance_score=significance_score,
        )
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def add_metric_trace(
        self,
        study_id: UUID,
        metric_dimension: str,
        observed_value: float,
        z_score: float = 0.0,
        p_value: float = 0.05,
    ) -> SingleMoleculeFretPolymeraseFidelityTrackerMetricTrace:
        trace = SingleMoleculeFretPolymeraseFidelityTrackerMetricTrace(
            study_id=study_id,
            metric_dimension=metric_dimension,
            observed_value=observed_value,
            z_score=z_score,
            p_value=p_value,
        )
        self.session.add(trace)
        await self.session.commit()
        await self.session.refresh(trace)
        return trace
