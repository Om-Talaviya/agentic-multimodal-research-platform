"""Repository for Phase 522: Autonomous Expansion Super-Resolution Optical Cryo-Correlative Multimodal Profiler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.super_resolution_expansion_cryo_microscopy import (
    SuperResolutionExpansionCryoMicroscopyStudy,
    SuperResolutionExpansionCryoMicroscopyItemProfile,
    SuperResolutionExpansionCryoMicroscopyMetricTrace,
)


class SuperResolutionExpansionCryoMicroscopyRepository:
    """Database operations for Autonomous Expansion Super-Resolution Optical Cryo-Correlative Multimodal Profiler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "4x Polyacrylate Hydrogel Swollen Vitrified Mouse Hippocampal Synapse with Pre- and Post-Synaptic Markers",
        analytical_modality: str = "cryo-expansion-super-resolution",
        effective_isotropic_optical_resolution_nm: float = 14.5,
        macromolecular_isotropy_expansion_factor: float = 4.15,
        fluorescent_label_retention_efficiency_pct: float = 92.0,
        clem_spatial_registration_fiducial_error_nm: float = 8.5,
        confidence_score: float = 0.995,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SuperResolutionExpansionCryoMicroscopyStudy:
        study = SuperResolutionExpansionCryoMicroscopyStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            effective_isotropic_optical_resolution_nm=effective_isotropic_optical_resolution_nm,
            macromolecular_isotropy_expansion_factor=macromolecular_isotropy_expansion_factor,
            fluorescent_label_retention_efficiency_pct=fluorescent_label_retention_efficiency_pct,
            clem_spatial_registration_fiducial_error_nm=clem_spatial_registration_fiducial_error_nm,
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
    ) -> SuperResolutionExpansionCryoMicroscopyItemProfile:
        item = SuperResolutionExpansionCryoMicroscopyItemProfile(
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
    ) -> SuperResolutionExpansionCryoMicroscopyMetricTrace:
        trace = SuperResolutionExpansionCryoMicroscopyMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SuperResolutionExpansionCryoMicroscopyStudy]:
        result = await self.session.execute(
            select(SuperResolutionExpansionCryoMicroscopyStudy)
            .options(
                selectinload(SuperResolutionExpansionCryoMicroscopyStudy.item_profiles),
                selectinload(SuperResolutionExpansionCryoMicroscopyStudy.metric_traces),
            )
            .where(SuperResolutionExpansionCryoMicroscopyStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[SuperResolutionExpansionCryoMicroscopyStudy]:
        result = await self.session.execute(
            select(SuperResolutionExpansionCryoMicroscopyStudy)
            .options(
                selectinload(SuperResolutionExpansionCryoMicroscopyStudy.item_profiles),
                selectinload(SuperResolutionExpansionCryoMicroscopyStudy.metric_traces),
            )
            .order_by(SuperResolutionExpansionCryoMicroscopyStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
