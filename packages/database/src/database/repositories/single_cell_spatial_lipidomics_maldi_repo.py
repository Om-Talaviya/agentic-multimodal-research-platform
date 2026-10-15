"""Repository for Phase 532: Autonomous High-Mass-Resolution MALDI MSI Single-Cell Spatial Phospholipid Fingerprinter."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.single_cell_spatial_lipidomics_maldi import (
    SingleCellSpatialLipidomicsMaldiStudy,
    SingleCellSpatialLipidomicsMaldiItemProfile,
    SingleCellSpatialLipidomicsMaldiMetricTrace,
)


class SingleCellSpatialLipidomicsMaldiRepository:
    """Database operations for Autonomous High-Mass-Resolution MALDI MSI Single-Cell Spatial Phospholipid Fingerprinter."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "High-Precision Cryo-Sectioned Mouse Brain Cortical Layer with 5um Sub-Cellular Laser Spot",
        analytical_modality: str = "single-cell-maldi-lipidomics",
        phospholipid_species_resolved_count: float = 385.0,
        spatial_laser_ablation_pitch_um: float = 5.0,
        mass_resolving_power_fwhm_at_m_z_800: float = 140000.0,
        cell_type_lipidomic_silhouette_score: float = 0.89,
        confidence_score: float = 0.995,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SingleCellSpatialLipidomicsMaldiStudy:
        study = SingleCellSpatialLipidomicsMaldiStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            phospholipid_species_resolved_count=phospholipid_species_resolved_count,
            spatial_laser_ablation_pitch_um=spatial_laser_ablation_pitch_um,
            mass_resolving_power_fwhm_at_m_z_800=mass_resolving_power_fwhm_at_m_z_800,
            cell_type_lipidomic_silhouette_score=cell_type_lipidomic_silhouette_score,
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
    ) -> SingleCellSpatialLipidomicsMaldiItemProfile:
        item = SingleCellSpatialLipidomicsMaldiItemProfile(
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
    ) -> SingleCellSpatialLipidomicsMaldiMetricTrace:
        trace = SingleCellSpatialLipidomicsMaldiMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SingleCellSpatialLipidomicsMaldiStudy]:
        stmt = (
            select(SingleCellSpatialLipidomicsMaldiStudy)
            .where(SingleCellSpatialLipidomicsMaldiStudy.id == study_id)
            .options(
                selectinload(SingleCellSpatialLipidomicsMaldiStudy.item_profiles),
                selectinload(SingleCellSpatialLipidomicsMaldiStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[SingleCellSpatialLipidomicsMaldiStudy]:
        stmt = (
            select(SingleCellSpatialLipidomicsMaldiStudy)
            .order_by(SingleCellSpatialLipidomicsMaldiStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(SingleCellSpatialLipidomicsMaldiStudy.item_profiles),
                selectinload(SingleCellSpatialLipidomicsMaldiStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
