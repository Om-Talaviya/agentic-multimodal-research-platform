"""Repository for Phase 491: Autonomous Biomimetic Synthetic Membrane Water Aquaporin Channel Transport Forecaster."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.aquaporin_biomimetic_water_transport import (
    AquaporinBiomimeticWaterTransportStudy,
    AquaporinBiomimeticWaterTransportItemProfile,
    AquaporinBiomimeticWaterTransportMetricTrace,
)


class AquaporinBiomimeticWaterTransportRepository:
    """Database operations for Autonomous Biomimetic Synthetic Membrane Water Aquaporin Channel Transport Forecaster."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Polymer-Inorganic Biomimetic Aquaporin-Z Nanocomposite Membrane with Forward Osmosis Crossflow",
        analytical_modality: str = "aquaporin-biomimetic-transport",
        water_permeability_flux_lmh_bar: float = 48.5,
        nacl_solute_rejection_percentage: float = 99.4,
        aquaporin_channel_incorporation_density_per_um2: float = 12500.0,
        single_pore_osmotic_permeability_pf_cm3_per_s: float = 4.2e-14,
        confidence_score: float = 0.992,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> AquaporinBiomimeticWaterTransportStudy:
        study = AquaporinBiomimeticWaterTransportStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            water_permeability_flux_lmh_bar=water_permeability_flux_lmh_bar,
            nacl_solute_rejection_percentage=nacl_solute_rejection_percentage,
            aquaporin_channel_incorporation_density_per_um2=aquaporin_channel_incorporation_density_per_um2,
            single_pore_osmotic_permeability_pf_cm3_per_s=single_pore_osmotic_permeability_pf_cm3_per_s,
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
    ) -> AquaporinBiomimeticWaterTransportItemProfile:
        item = AquaporinBiomimeticWaterTransportItemProfile(
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
    ) -> AquaporinBiomimeticWaterTransportMetricTrace:
        trace = AquaporinBiomimeticWaterTransportMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[AquaporinBiomimeticWaterTransportStudy]:
        result = await self.session.execute(
            select(AquaporinBiomimeticWaterTransportStudy)
            .options(
                selectinload(AquaporinBiomimeticWaterTransportStudy.item_profiles),
                selectinload(AquaporinBiomimeticWaterTransportStudy.metric_traces),
            )
            .where(AquaporinBiomimeticWaterTransportStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[AquaporinBiomimeticWaterTransportStudy]:
        result = await self.session.execute(
            select(AquaporinBiomimeticWaterTransportStudy)
            .options(
                selectinload(AquaporinBiomimeticWaterTransportStudy.item_profiles),
                selectinload(AquaporinBiomimeticWaterTransportStudy.metric_traces),
            )
            .order_by(AquaporinBiomimeticWaterTransportStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
