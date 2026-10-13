"""Repository for Phase 460: Autonomous In-Situ Cryo-CLEM Fluorescent Target Correlation & Precision Fiducial Alignment Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cryo_clem_fiducial_alignment import (
    CryoClemFiducialAlignmentStudy,
    CryoClemFiducialAlignmentItemProfile,
    CryoClemFiducialAlignmentMetricTrace,
)


class CryoClemFiducialAlignmentRepository:
    """Database operations for Autonomous In-Situ Cryo-CLEM Fluorescent Target Correlation & Precision Fiducial Alignment Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Vitrified Primary Axon Growth Cone with Gold Nanoparticle Fiducials and GFP-Tagged Cargo",
        analytical_modality: str = "cryo-clem-fiducial-alignment",
        coordinate_transformation_target_registration_error_nm: float = 28.5,
        fiducial_triangulation_residual_angstrom: float = 18.2,
        fluorescence_cryo_snr_decibels: float = 24.6,
        target_feature_hit_probability: float = 0.965,
        confidence_score: float = 0.993,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CryoClemFiducialAlignmentStudy:
        study = CryoClemFiducialAlignmentStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            coordinate_transformation_target_registration_error_nm=coordinate_transformation_target_registration_error_nm,
            fiducial_triangulation_residual_angstrom=fiducial_triangulation_residual_angstrom,
            fluorescence_cryo_snr_decibels=fluorescence_cryo_snr_decibels,
            target_feature_hit_probability=target_feature_hit_probability,
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
    ) -> CryoClemFiducialAlignmentItemProfile:
        item = CryoClemFiducialAlignmentItemProfile(
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
    ) -> CryoClemFiducialAlignmentMetricTrace:
        trace = CryoClemFiducialAlignmentMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CryoClemFiducialAlignmentStudy]:
        result = await self.session.execute(
            select(CryoClemFiducialAlignmentStudy)
            .options(
                selectinload(CryoClemFiducialAlignmentStudy.item_profiles),
                selectinload(CryoClemFiducialAlignmentStudy.metric_traces),
            )
            .where(CryoClemFiducialAlignmentStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[CryoClemFiducialAlignmentStudy]:
        result = await self.session.execute(
            select(CryoClemFiducialAlignmentStudy)
            .options(
                selectinload(CryoClemFiducialAlignmentStudy.item_profiles),
                selectinload(CryoClemFiducialAlignmentStudy.metric_traces),
            )
            .order_by(CryoClemFiducialAlignmentStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
