"""Repository for Phase 516: Autonomous Automated High-Throughput Mass Photometry Macromolecular Mass Dispersity Profiler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.high_throughput_mass_photometry_ribosome import (
    HighThroughputMassPhotometryRibosomeStudy,
    HighThroughputMassPhotometryRibosomeItemProfile,
    HighThroughputMassPhotometryRibosomeMetricTrace,
)


class HighThroughputMassPhotometryRibosomeRepository:
    """Database operations for Autonomous Automated High-Throughput Mass Photometry Macromolecular Mass Dispersity Profiler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Label-Free Reconstituted 70S Ribosome Assembly Intermediates with Initiation Factors IF1/IF2/IF3",
        analytical_modality: str = "mass-photometry-single-molecule-scattering",
        molecular_mass_resolution_error_pct: float = 1.25,
        subassembly_stoichiometric_ratio_30s_50s_70s: float = 1.05,
        single_molecule_scattering_interferometric_contrast: float = 0.0085,
        sample_consumption_volume_nanoliters: float = 50.0,
        confidence_score: float = 0.994,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> HighThroughputMassPhotometryRibosomeStudy:
        study = HighThroughputMassPhotometryRibosomeStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            molecular_mass_resolution_error_pct=molecular_mass_resolution_error_pct,
            subassembly_stoichiometric_ratio_30s_50s_70s=subassembly_stoichiometric_ratio_30s_50s_70s,
            single_molecule_scattering_interferometric_contrast=single_molecule_scattering_interferometric_contrast,
            sample_consumption_volume_nanoliters=sample_consumption_volume_nanoliters,
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
    ) -> HighThroughputMassPhotometryRibosomeItemProfile:
        item = HighThroughputMassPhotometryRibosomeItemProfile(
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
    ) -> HighThroughputMassPhotometryRibosomeMetricTrace:
        trace = HighThroughputMassPhotometryRibosomeMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[HighThroughputMassPhotometryRibosomeStudy]:
        result = await self.session.execute(
            select(HighThroughputMassPhotometryRibosomeStudy)
            .options(
                selectinload(HighThroughputMassPhotometryRibosomeStudy.item_profiles),
                selectinload(HighThroughputMassPhotometryRibosomeStudy.metric_traces),
            )
            .where(HighThroughputMassPhotometryRibosomeStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[HighThroughputMassPhotometryRibosomeStudy]:
        result = await self.session.execute(
            select(HighThroughputMassPhotometryRibosomeStudy)
            .options(
                selectinload(HighThroughputMassPhotometryRibosomeStudy.item_profiles),
                selectinload(HighThroughputMassPhotometryRibosomeStudy.metric_traces),
            )
            .order_by(HighThroughputMassPhotometryRibosomeStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
