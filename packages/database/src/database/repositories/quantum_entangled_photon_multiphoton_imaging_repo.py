"""Repository for Phase 565: Autonomous Quantum Entangled Photon Biological Tissue Multiphoton Imaging Resolution Maximizer."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.quantum_entangled_photon_multiphoton_imaging import (
    QuantumEntangledPhotonMultiphotonImagingStudy,
    QuantumEntangledPhotonMultiphotonImagingItemProfile,
    QuantumEntangledPhotonMultiphotonImagingMetricTrace,
)


class QuantumEntangledPhotonMultiphotonImagingRepository:
    """Database operations for Autonomous Quantum Entangled Photon Biological Tissue Multiphoton Imaging Resolution Maximizer."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Intact Vitrified Mouse Cortical Brain Slices illuminated with Polarization-Entangled Photon Pairs at 800nm",
        analytical_modality: str = "entangled-photon-multiphoton",
        two_photon_absorption_cross_section_enhancement_fold: float = 185.0,
        imaging_tissue_penetration_depth_um: float = 950.0,
        photobleaching_rate_suppression_pct: float = 88.5,
        quantum_sub_shot_noise_snr_gain_db: float = 5.4,
        confidence_score: float = 0.998,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> QuantumEntangledPhotonMultiphotonImagingStudy:
        study = QuantumEntangledPhotonMultiphotonImagingStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            two_photon_absorption_cross_section_enhancement_fold=two_photon_absorption_cross_section_enhancement_fold,
            imaging_tissue_penetration_depth_um=imaging_tissue_penetration_depth_um,
            photobleaching_rate_suppression_pct=photobleaching_rate_suppression_pct,
            quantum_sub_shot_noise_snr_gain_db=quantum_sub_shot_noise_snr_gain_db,
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
    ) -> QuantumEntangledPhotonMultiphotonImagingItemProfile:
        item = QuantumEntangledPhotonMultiphotonImagingItemProfile(
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
    ) -> QuantumEntangledPhotonMultiphotonImagingMetricTrace:
        trace = QuantumEntangledPhotonMultiphotonImagingMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[QuantumEntangledPhotonMultiphotonImagingStudy]:
        stmt = (
            select(QuantumEntangledPhotonMultiphotonImagingStudy)
            .where(QuantumEntangledPhotonMultiphotonImagingStudy.id == study_id)
            .options(
                selectinload(QuantumEntangledPhotonMultiphotonImagingStudy.item_profiles),
                selectinload(QuantumEntangledPhotonMultiphotonImagingStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[QuantumEntangledPhotonMultiphotonImagingStudy]:
        stmt = (
            select(QuantumEntangledPhotonMultiphotonImagingStudy)
            .order_by(QuantumEntangledPhotonMultiphotonImagingStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(QuantumEntangledPhotonMultiphotonImagingStudy.item_profiles),
                selectinload(QuantumEntangledPhotonMultiphotonImagingStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
