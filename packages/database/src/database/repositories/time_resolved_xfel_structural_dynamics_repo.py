"""Repository for Phase 557: Autonomous Time-Resolved Femtosecond X-ray Free-Electron Laser (XFEL) Macromolecular Structural Dynamics Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.time_resolved_xfel_structural_dynamics import (
    TimeResolvedXfelStructuralDynamicsStudy,
    TimeResolvedXfelStructuralDynamicsItemProfile,
    TimeResolvedXfelStructuralDynamicsMetricTrace,
)


class TimeResolvedXfelStructuralDynamicsRepository:
    """Database operations for Autonomous Time-Resolved Femtosecond X-ray Free-Electron Laser (XFEL) Macromolecular Structural Dynamics Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Photoactive Yellow Protein (PYP) Microcrystals probed by 10-fs X-ray Pulses at LCLS-II after 450nm Laser Photolysis",
        analytical_modality: str = "time-resolved-xfel-dynamics",
        femtosecond_temporal_resolution_fs: float = 85.0,
        chromophore_trans_to_cis_isomerization_time_ps: float = 1.45,
        difference_electron_density_signal_snr: float = 28.5,
        serial_femtosecond_crystallography_resolution_a: float = 1.35,
        confidence_score: float = 0.997,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> TimeResolvedXfelStructuralDynamicsStudy:
        study = TimeResolvedXfelStructuralDynamicsStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            femtosecond_temporal_resolution_fs=femtosecond_temporal_resolution_fs,
            chromophore_trans_to_cis_isomerization_time_ps=chromophore_trans_to_cis_isomerization_time_ps,
            difference_electron_density_signal_snr=difference_electron_density_signal_snr,
            serial_femtosecond_crystallography_resolution_a=serial_femtosecond_crystallography_resolution_a,
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
    ) -> TimeResolvedXfelStructuralDynamicsItemProfile:
        item = TimeResolvedXfelStructuralDynamicsItemProfile(
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
    ) -> TimeResolvedXfelStructuralDynamicsMetricTrace:
        trace = TimeResolvedXfelStructuralDynamicsMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[TimeResolvedXfelStructuralDynamicsStudy]:
        stmt = (
            select(TimeResolvedXfelStructuralDynamicsStudy)
            .where(TimeResolvedXfelStructuralDynamicsStudy.id == study_id)
            .options(
                selectinload(TimeResolvedXfelStructuralDynamicsStudy.item_profiles),
                selectinload(TimeResolvedXfelStructuralDynamicsStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[TimeResolvedXfelStructuralDynamicsStudy]:
        stmt = (
            select(TimeResolvedXfelStructuralDynamicsStudy)
            .order_by(TimeResolvedXfelStructuralDynamicsStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(TimeResolvedXfelStructuralDynamicsStudy.item_profiles),
                selectinload(TimeResolvedXfelStructuralDynamicsStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
