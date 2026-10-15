"""Repository for Phase 544: Autonomous Integrated Cryo-CLEM High-Precision 3D Sub-Diffraction Nanoscale Fiducial Correlator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cryo_correlative_light_electron_tomography_clem import (
    CryoCorrelativeLightElectronTomographyClemStudy,
    CryoCorrelativeLightElectronTomographyClemItemProfile,
    CryoCorrelativeLightElectronTomographyClemMetricTrace,
)


class CryoCorrelativeLightElectronTomographyClemRepository:
    """Database operations for Autonomous Integrated Cryo-CLEM High-Precision 3D Sub-Diffraction Nanoscale Fiducial Correlator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Cryo-Vitrified Neuronal Cultured Grid with Tetraspeck Fluorescent Nanobeads and Sub-10nm Gold Fiducials",
        analytical_modality: str = "cryo-clem-fiducial-correlation",
        cross_modality_3d_registration_precision_nm: float = 12.2,
        cryo_fluorescence_signal_to_background_ratio: float = 48.5,
        cryo_fib_milling_target_accuracy_nm: float = 24.0,
        subtomogram_correlation_coefficient: float = 0.925,
        confidence_score: float = 0.996,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CryoCorrelativeLightElectronTomographyClemStudy:
        study = CryoCorrelativeLightElectronTomographyClemStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            cross_modality_3d_registration_precision_nm=cross_modality_3d_registration_precision_nm,
            cryo_fluorescence_signal_to_background_ratio=cryo_fluorescence_signal_to_background_ratio,
            cryo_fib_milling_target_accuracy_nm=cryo_fib_milling_target_accuracy_nm,
            subtomogram_correlation_coefficient=subtomogram_correlation_coefficient,
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
    ) -> CryoCorrelativeLightElectronTomographyClemItemProfile:
        item = CryoCorrelativeLightElectronTomographyClemItemProfile(
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
    ) -> CryoCorrelativeLightElectronTomographyClemMetricTrace:
        trace = CryoCorrelativeLightElectronTomographyClemMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CryoCorrelativeLightElectronTomographyClemStudy]:
        stmt = (
            select(CryoCorrelativeLightElectronTomographyClemStudy)
            .where(CryoCorrelativeLightElectronTomographyClemStudy.id == study_id)
            .options(
                selectinload(CryoCorrelativeLightElectronTomographyClemStudy.item_profiles),
                selectinload(CryoCorrelativeLightElectronTomographyClemStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[CryoCorrelativeLightElectronTomographyClemStudy]:
        stmt = (
            select(CryoCorrelativeLightElectronTomographyClemStudy)
            .order_by(CryoCorrelativeLightElectronTomographyClemStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(CryoCorrelativeLightElectronTomographyClemStudy.item_profiles),
                selectinload(CryoCorrelativeLightElectronTomographyClemStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
