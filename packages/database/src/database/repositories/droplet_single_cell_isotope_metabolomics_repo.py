"""Repository for Phase 449: Autonomous Microfluidic Droplet Single-Cell Metabolic Metabolomics Isotope Labeling Profiler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.droplet_single_cell_isotope_metabolomics import (
    DropletSingleCellIsotopeMetabolomicsStudy,
    DropletSingleCellIsotopeMetabolomicsItemProfile,
    DropletSingleCellIsotopeMetabolomicsMetricTrace,
)


class DropletSingleCellIsotopeMetabolomicsRepository:
    """Database operations for Autonomous Microfluidic Droplet Single-Cell Metabolic Metabolomics Isotope Labeling Profiler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Glucose-13C6 Labeled Glioblastoma Stem-Like Cells in Monodisperse Fluorocarbon Droplets",
        analytical_modality: str = "single-cell-droplet-metabolomics",
        isotopic_enrichment_m3_lactate_ratio: float = 0.765,
        droplet_generation_frequency_khz: float = 4.8,
        glycolytic_flux_attomoles_per_cell_min: float = 38.5,
        mass_accuracy_orbitrap_ppm: float = 0.85,
        confidence_score: float = 0.989,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> DropletSingleCellIsotopeMetabolomicsStudy:
        study = DropletSingleCellIsotopeMetabolomicsStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            isotopic_enrichment_m3_lactate_ratio=isotopic_enrichment_m3_lactate_ratio,
            droplet_generation_frequency_khz=droplet_generation_frequency_khz,
            glycolytic_flux_attomoles_per_cell_min=glycolytic_flux_attomoles_per_cell_min,
            mass_accuracy_orbitrap_ppm=mass_accuracy_orbitrap_ppm,
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
    ) -> DropletSingleCellIsotopeMetabolomicsItemProfile:
        item = DropletSingleCellIsotopeMetabolomicsItemProfile(
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
    ) -> DropletSingleCellIsotopeMetabolomicsMetricTrace:
        trace = DropletSingleCellIsotopeMetabolomicsMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[DropletSingleCellIsotopeMetabolomicsStudy]:
        result = await self.session.execute(
            select(DropletSingleCellIsotopeMetabolomicsStudy)
            .options(
                selectinload(DropletSingleCellIsotopeMetabolomicsStudy.item_profiles),
                selectinload(DropletSingleCellIsotopeMetabolomicsStudy.metric_traces),
            )
            .where(DropletSingleCellIsotopeMetabolomicsStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DropletSingleCellIsotopeMetabolomicsStudy]:
        result = await self.session.execute(
            select(DropletSingleCellIsotopeMetabolomicsStudy)
            .options(
                selectinload(DropletSingleCellIsotopeMetabolomicsStudy.item_profiles),
                selectinload(DropletSingleCellIsotopeMetabolomicsStudy.metric_traces),
            )
            .order_by(DropletSingleCellIsotopeMetabolomicsStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
