"""Repository for Phase 559: Autonomous Biohybrid Microbial Fuel Cell Extracellular Electron Shuttle Redox Kinetics Simulator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.biohybrid_microbial_fuel_cell_redox import (
    BiohybridMicrobialFuelCellRedoxStudy,
    BiohybridMicrobialFuelCellRedoxItemProfile,
    BiohybridMicrobialFuelCellRedoxMetricTrace,
)


class BiohybridMicrobialFuelCellRedoxRepository:
    """Database operations for Autonomous Biohybrid Microbial Fuel Cell Extracellular Electron Shuttle Redox Kinetics Simulator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Shewanella oneidensis MR-1 living Biofilm grown on 3D Carbon Nanotube Anode with Riboflavin Redox Mediators",
        analytical_modality: str = "biohybrid-microbial-fuel-cell",
        anodic_current_density_ma_cm2: float = 14.8,
        extracellular_electron_transfer_rate_per_sec: float = 820.0,
        cytochrome_mtrc_reduction_potential_mv: float = -140.0,
        fuel_cell_maximum_power_density_mw_m2: float = 2450.0,
        confidence_score: float = 0.994,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> BiohybridMicrobialFuelCellRedoxStudy:
        study = BiohybridMicrobialFuelCellRedoxStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            anodic_current_density_ma_cm2=anodic_current_density_ma_cm2,
            extracellular_electron_transfer_rate_per_sec=extracellular_electron_transfer_rate_per_sec,
            cytochrome_mtrc_reduction_potential_mv=cytochrome_mtrc_reduction_potential_mv,
            fuel_cell_maximum_power_density_mw_m2=fuel_cell_maximum_power_density_mw_m2,
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
    ) -> BiohybridMicrobialFuelCellRedoxItemProfile:
        item = BiohybridMicrobialFuelCellRedoxItemProfile(
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
    ) -> BiohybridMicrobialFuelCellRedoxMetricTrace:
        trace = BiohybridMicrobialFuelCellRedoxMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[BiohybridMicrobialFuelCellRedoxStudy]:
        stmt = (
            select(BiohybridMicrobialFuelCellRedoxStudy)
            .where(BiohybridMicrobialFuelCellRedoxStudy.id == study_id)
            .options(
                selectinload(BiohybridMicrobialFuelCellRedoxStudy.item_profiles),
                selectinload(BiohybridMicrobialFuelCellRedoxStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[BiohybridMicrobialFuelCellRedoxStudy]:
        stmt = (
            select(BiohybridMicrobialFuelCellRedoxStudy)
            .order_by(BiohybridMicrobialFuelCellRedoxStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(BiohybridMicrobialFuelCellRedoxStudy.item_profiles),
                selectinload(BiohybridMicrobialFuelCellRedoxStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
