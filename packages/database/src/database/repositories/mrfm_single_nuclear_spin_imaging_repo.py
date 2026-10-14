"""Repository for Phase 499: Autonomous Single-Molecule Magnetic Resonance Force Microscopy 3D Nuclear Spin Imaging Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.mrfm_single_nuclear_spin_imaging import (
    MrfmSingleNuclearSpinImagingStudy,
    MrfmSingleNuclearSpinImagingItemProfile,
    MrfmSingleNuclearSpinImagingMetricTrace,
)


class MrfmSingleNuclearSpinImagingRepository:
    """Database operations for Autonomous Single-Molecule Magnetic Resonance Force Microscopy 3D Nuclear Spin Imaging Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Ultra-Sensitive Silicon Nanocantilever with Ferromagnetic SmCo Tip over Vitrified Tobacco Mosaic Virus",
        analytical_modality: str = "mrfm-single-spin-imaging",
        mrfm_spatial_resolution_nm: float = 1.85,
        attonewton_force_gradient_sensitivity_aN_per_nm: float = 4.2,
        spin_nutation_inversion_fidelity: float = 0.985,
        three_d_spin_density_reconstruction_snr: float = 19.4,
        confidence_score: float = 0.993,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MrfmSingleNuclearSpinImagingStudy:
        study = MrfmSingleNuclearSpinImagingStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            mrfm_spatial_resolution_nm=mrfm_spatial_resolution_nm,
            attonewton_force_gradient_sensitivity_aN_per_nm=attonewton_force_gradient_sensitivity_aN_per_nm,
            spin_nutation_inversion_fidelity=spin_nutation_inversion_fidelity,
            three_d_spin_density_reconstruction_snr=three_d_spin_density_reconstruction_snr,
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
    ) -> MrfmSingleNuclearSpinImagingItemProfile:
        item = MrfmSingleNuclearSpinImagingItemProfile(
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
    ) -> MrfmSingleNuclearSpinImagingMetricTrace:
        trace = MrfmSingleNuclearSpinImagingMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MrfmSingleNuclearSpinImagingStudy]:
        result = await self.session.execute(
            select(MrfmSingleNuclearSpinImagingStudy)
            .options(
                selectinload(MrfmSingleNuclearSpinImagingStudy.item_profiles),
                selectinload(MrfmSingleNuclearSpinImagingStudy.metric_traces),
            )
            .where(MrfmSingleNuclearSpinImagingStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[MrfmSingleNuclearSpinImagingStudy]:
        result = await self.session.execute(
            select(MrfmSingleNuclearSpinImagingStudy)
            .options(
                selectinload(MrfmSingleNuclearSpinImagingStudy.item_profiles),
                selectinload(MrfmSingleNuclearSpinImagingStudy.metric_traces),
            )
            .order_by(MrfmSingleNuclearSpinImagingStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
