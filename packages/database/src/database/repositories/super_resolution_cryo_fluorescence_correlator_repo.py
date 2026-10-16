"""Repository for Phase 569: Autonomous In-Situ Cryo-Correlative Super-Resolution Cryo-Fluorescence & Cryo-ET Single-Molecule Spatial Registration Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.super_resolution_cryo_fluorescence_correlator import (
    SuperResolutionCryoFluorescenceCorrelatorStudy,
    SuperResolutionCryoFluorescenceCorrelatorItemProfile,
    SuperResolutionCryoFluorescenceCorrelatorMetricTrace,
)


class SuperResolutionCryoFluorescenceCorrelatorRepository:
    """Repository for Autonomous In-Situ Cryo-Correlative Super-Resolution Cryo-Fluorescence & Cryo-ET Single-Molecule Spatial Registration Engine storage and retrieval."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str,
        analytical_modality: str,
        fiducial_registration_precision_nm: float,
        photobleaching_threshold_flux_kw_cm2: float,
        localization_confidence_score: float,
        cryo_optical_drift_variance_nm2: float,
        confidence_score: float = 0.996,
        status: str = "completed",
        summary_report: Optional[str] = None,
        parameters: Optional[dict] = None,
    ) -> SuperResolutionCryoFluorescenceCorrelatorStudy:
        study = SuperResolutionCryoFluorescenceCorrelatorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            fiducial_registration_precision_nm=fiducial_registration_precision_nm,
            photobleaching_threshold_flux_kw_cm2=photobleaching_threshold_flux_kw_cm2,
            localization_confidence_score=localization_confidence_score,
            cryo_optical_drift_variance_nm2=cryo_optical_drift_variance_nm2,
            confidence_score=confidence_score,
            status=status,
            summary_report=summary_report,
            parameters=parameters or {},
        )
        self.session.add(study)
        await self.session.commit()
        await self.session.refresh(study)
        return study

    async def get_study(self, study_id: UUID) -> Optional[SuperResolutionCryoFluorescenceCorrelatorStudy]:
        stmt = select(SuperResolutionCryoFluorescenceCorrelatorStudy).where(SuperResolutionCryoFluorescenceCorrelatorStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[SuperResolutionCryoFluorescenceCorrelatorStudy]:
        stmt = select(SuperResolutionCryoFluorescenceCorrelatorStudy).order_by(SuperResolutionCryoFluorescenceCorrelatorStudy.created_at.desc()).limit(limit)
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
    ) -> SuperResolutionCryoFluorescenceCorrelatorItemProfile:
        profile = SuperResolutionCryoFluorescenceCorrelatorItemProfile(
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
    ) -> SuperResolutionCryoFluorescenceCorrelatorMetricTrace:
        trace = SuperResolutionCryoFluorescenceCorrelatorMetricTrace(
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
