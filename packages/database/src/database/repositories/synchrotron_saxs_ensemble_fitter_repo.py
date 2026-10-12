"""Repository for Phase 433: Autonomous Synchrotron Small-Angle X-ray Scattering (SAXS) Ensemble Conformational Fitting Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.synchrotron_saxs_ensemble_fitter import (
    SynchrotronSaxsEnsembleFitterStudy,
    SynchrotronSaxsEnsembleFitterItemProfile,
    SynchrotronSaxsEnsembleFitterMetricTrace,
)


class SynchrotronSaxsEnsembleFitterRepository:
    """Database operations for Autonomous Synchrotron Small-Angle X-ray Scattering (SAXS) Ensemble Conformational Fitting Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Intrinsically Disordered Kinase Domain in Solution",
        analytical_modality: str = "synchrotron-saxs",
        radius_of_gyration_Rg_angstrom: float = 34.2,
        kratky_plot_flexibility_index: float = 0.895,
        ensemble_fit_chi_squared: float = 1.08,
        maximum_particle_dimension_Dmax_angstrom: float = 112.0,
        confidence_score: float = 0.991,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SynchrotronSaxsEnsembleFitterStudy:
        study = SynchrotronSaxsEnsembleFitterStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            radius_of_gyration_Rg_angstrom=radius_of_gyration_Rg_angstrom,
            kratky_plot_flexibility_index=kratky_plot_flexibility_index,
            ensemble_fit_chi_squared=ensemble_fit_chi_squared,
            maximum_particle_dimension_Dmax_angstrom=maximum_particle_dimension_Dmax_angstrom,
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
    ) -> SynchrotronSaxsEnsembleFitterItemProfile:
        item = SynchrotronSaxsEnsembleFitterItemProfile(
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
    ) -> SynchrotronSaxsEnsembleFitterMetricTrace:
        trace = SynchrotronSaxsEnsembleFitterMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SynchrotronSaxsEnsembleFitterStudy]:
        result = await self.session.execute(
            select(SynchrotronSaxsEnsembleFitterStudy)
            .options(
                selectinload(SynchrotronSaxsEnsembleFitterStudy.item_profiles),
                selectinload(SynchrotronSaxsEnsembleFitterStudy.metric_traces),
            )
            .where(SynchrotronSaxsEnsembleFitterStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[SynchrotronSaxsEnsembleFitterStudy]:
        result = await self.session.execute(
            select(SynchrotronSaxsEnsembleFitterStudy)
            .options(
                selectinload(SynchrotronSaxsEnsembleFitterStudy.item_profiles),
                selectinload(SynchrotronSaxsEnsembleFitterStudy.metric_traces),
            )
            .order_by(SynchrotronSaxsEnsembleFitterStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
