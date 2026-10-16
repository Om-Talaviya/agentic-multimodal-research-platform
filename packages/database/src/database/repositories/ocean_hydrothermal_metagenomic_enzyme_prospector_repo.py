"""Repository for Phase 561: Autonomous High-Throughput Deep Ocean Hydrothermal Vent Metagenomic Novel Enzyme Prospector."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.ocean_hydrothermal_metagenomic_enzyme_prospector import (
    OceanHydrothermalMetagenomicEnzymeProspectorStudy,
    OceanHydrothermalMetagenomicEnzymeProspectorItemProfile,
    OceanHydrothermalMetagenomicEnzymeProspectorMetricTrace,
)


class OceanHydrothermalMetagenomicEnzymeProspectorRepository:
    """Database operations for Autonomous High-Throughput Deep Ocean Hydrothermal Vent Metagenomic Novel Enzyme Prospector."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Deep-Sea Metagenomic DNA from Mid-Atlantic Ridge Black Smoker Vent Hydrothermal Fluid at 320C and 300 Bar",
        analytical_modality: str = "deep-sea-metagenomic-biocatalysis",
        thermostable_extremozyme_catalytic_half_life_hours: float = 72.0,
        novel_biocatalytic_family_discovery_count: float = 34.0,
        piezophilic_activation_volume_delta_v_ml_mol: float = -28.5,
        optimum_catalytic_temperature_celsius: float = 108.5,
        confidence_score: float = 0.995,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> OceanHydrothermalMetagenomicEnzymeProspectorStudy:
        study = OceanHydrothermalMetagenomicEnzymeProspectorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            thermostable_extremozyme_catalytic_half_life_hours=thermostable_extremozyme_catalytic_half_life_hours,
            novel_biocatalytic_family_discovery_count=novel_biocatalytic_family_discovery_count,
            piezophilic_activation_volume_delta_v_ml_mol=piezophilic_activation_volume_delta_v_ml_mol,
            optimum_catalytic_temperature_celsius=optimum_catalytic_temperature_celsius,
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
    ) -> OceanHydrothermalMetagenomicEnzymeProspectorItemProfile:
        item = OceanHydrothermalMetagenomicEnzymeProspectorItemProfile(
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
    ) -> OceanHydrothermalMetagenomicEnzymeProspectorMetricTrace:
        trace = OceanHydrothermalMetagenomicEnzymeProspectorMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[OceanHydrothermalMetagenomicEnzymeProspectorStudy]:
        stmt = (
            select(OceanHydrothermalMetagenomicEnzymeProspectorStudy)
            .where(OceanHydrothermalMetagenomicEnzymeProspectorStudy.id == study_id)
            .options(
                selectinload(OceanHydrothermalMetagenomicEnzymeProspectorStudy.item_profiles),
                selectinload(OceanHydrothermalMetagenomicEnzymeProspectorStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[OceanHydrothermalMetagenomicEnzymeProspectorStudy]:
        stmt = (
            select(OceanHydrothermalMetagenomicEnzymeProspectorStudy)
            .order_by(OceanHydrothermalMetagenomicEnzymeProspectorStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(OceanHydrothermalMetagenomicEnzymeProspectorStudy.item_profiles),
                selectinload(OceanHydrothermalMetagenomicEnzymeProspectorStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
