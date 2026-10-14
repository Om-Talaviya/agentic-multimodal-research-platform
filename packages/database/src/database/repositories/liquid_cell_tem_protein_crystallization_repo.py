"""Repository for Phase 520: Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy Protein Nucleation Real-Time Tracker."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.liquid_cell_tem_protein_crystallization import (
    LiquidCellTemProteinCrystallizationStudy,
    LiquidCellTemProteinCrystallizationItemProfile,
    LiquidCellTemProteinCrystallizationMetricTrace,
)


class LiquidCellTemProteinCrystallizationRepository:
    """Database operations for Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy Protein Nucleation Real-Time Tracker."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Silicon Nitride Microchip Graphene Liquid Cell with Supersaturated Hen Egg-White Lysozyme Solution",
        analytical_modality: str = "liquid-cell-tem-crystallization",
        critical_nucleus_radius_nm: float = 2.4,
        non_classical_pre_nucleation_cluster_density_per_um3: float = 1250.0,
        crystal_facet_growth_rate_nm_per_min: float = 1.85,
        electron_beam_dose_induced_radiolysis_damage_threshold_e_per_angstrom2: float = 2.5,
        confidence_score: float = 0.994,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> LiquidCellTemProteinCrystallizationStudy:
        study = LiquidCellTemProteinCrystallizationStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            critical_nucleus_radius_nm=critical_nucleus_radius_nm,
            non_classical_pre_nucleation_cluster_density_per_um3=non_classical_pre_nucleation_cluster_density_per_um3,
            crystal_facet_growth_rate_nm_per_min=crystal_facet_growth_rate_nm_per_min,
            electron_beam_dose_induced_radiolysis_damage_threshold_e_per_angstrom2=electron_beam_dose_induced_radiolysis_damage_threshold_e_per_angstrom2,
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
    ) -> LiquidCellTemProteinCrystallizationItemProfile:
        item = LiquidCellTemProteinCrystallizationItemProfile(
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
    ) -> LiquidCellTemProteinCrystallizationMetricTrace:
        trace = LiquidCellTemProteinCrystallizationMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[LiquidCellTemProteinCrystallizationStudy]:
        result = await self.session.execute(
            select(LiquidCellTemProteinCrystallizationStudy)
            .options(
                selectinload(LiquidCellTemProteinCrystallizationStudy.item_profiles),
                selectinload(LiquidCellTemProteinCrystallizationStudy.metric_traces),
            )
            .where(LiquidCellTemProteinCrystallizationStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[LiquidCellTemProteinCrystallizationStudy]:
        result = await self.session.execute(
            select(LiquidCellTemProteinCrystallizationStudy)
            .options(
                selectinload(LiquidCellTemProteinCrystallizationStudy.item_profiles),
                selectinload(LiquidCellTemProteinCrystallizationStudy.metric_traces),
            )
            .order_by(LiquidCellTemProteinCrystallizationStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
