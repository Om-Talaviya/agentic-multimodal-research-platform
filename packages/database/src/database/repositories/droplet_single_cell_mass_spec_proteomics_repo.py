"""Repository for Phase 524: Autonomous Picoliter Microfluidic Droplet Single-Cell Mass Spectrometry Proteome Fingerprinter."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.droplet_single_cell_mass_spec_proteomics import (
    DropletSingleCellMassSpecProteomicsStudy,
    DropletSingleCellMassSpecProteomicsItemProfile,
    DropletSingleCellMassSpecProteomicsMetricTrace,
)


class DropletSingleCellMassSpecProteomicsRepository:
    """Database operations for Autonomous Picoliter Microfluidic Droplet Single-Cell Mass Spectrometry Proteome Fingerprinter."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Direct Microfluidic Nano-Electrospray Ionization (nanoESI) Orbitrap MS of Individual Single Glioblastoma Cells",
        analytical_modality: str = "droplet-single-cell-proteomics",
        quantified_proteins_per_single_cell_count: float = 2450.0,
        median_protein_sequence_coverage_pct: float = 28.5,
        sample_loss_reduction_surface_adsorption_pct: float = 94.0,
        single_cell_proteomic_profiling_throughput_cells_per_hr: float = 120.0,
        confidence_score: float = 0.994,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> DropletSingleCellMassSpecProteomicsStudy:
        study = DropletSingleCellMassSpecProteomicsStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            quantified_proteins_per_single_cell_count=quantified_proteins_per_single_cell_count,
            median_protein_sequence_coverage_pct=median_protein_sequence_coverage_pct,
            sample_loss_reduction_surface_adsorption_pct=sample_loss_reduction_surface_adsorption_pct,
            single_cell_proteomic_profiling_throughput_cells_per_hr=single_cell_proteomic_profiling_throughput_cells_per_hr,
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
    ) -> DropletSingleCellMassSpecProteomicsItemProfile:
        item = DropletSingleCellMassSpecProteomicsItemProfile(
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
    ) -> DropletSingleCellMassSpecProteomicsMetricTrace:
        trace = DropletSingleCellMassSpecProteomicsMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[DropletSingleCellMassSpecProteomicsStudy]:
        result = await self.session.execute(
            select(DropletSingleCellMassSpecProteomicsStudy)
            .options(
                selectinload(DropletSingleCellMassSpecProteomicsStudy.item_profiles),
                selectinload(DropletSingleCellMassSpecProteomicsStudy.metric_traces),
            )
            .where(DropletSingleCellMassSpecProteomicsStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DropletSingleCellMassSpecProteomicsStudy]:
        result = await self.session.execute(
            select(DropletSingleCellMassSpecProteomicsStudy)
            .options(
                selectinload(DropletSingleCellMassSpecProteomicsStudy.item_profiles),
                selectinload(DropletSingleCellMassSpecProteomicsStudy.metric_traces),
            )
            .order_by(DropletSingleCellMassSpecProteomicsStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
