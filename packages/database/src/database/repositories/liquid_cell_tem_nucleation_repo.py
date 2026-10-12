"""Repository for Phase 428: Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy (LC-TEM) Nanoparticle Nucleation Simulator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.liquid_cell_tem_nucleation import (
    LiquidCellTemNucleationStudy,
    LiquidCellTemNucleationItemProfile,
    LiquidCellTemNucleationMetricTrace,
)


class LiquidCellTemNucleationRepository:
    """Database operations for Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy (LC-TEM) Nanoparticle Nucleation Simulator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Silicon Nitride Liquid Cell with Gold Nanocrystal Growth Solution",
        analytical_modality: str = "liquid-cell-tem",
        nucleation_rate_particles_per_s_um2: float = 14.2,
        critical_nucleus_radius_nm: float = 1.45,
        non_classical_attachment_frequency: float = 0.785,
        electron_beam_dose_rate_e_per_ang2_s: float = 8.5,
        confidence_score: float = 0.984,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> LiquidCellTemNucleationStudy:
        study = LiquidCellTemNucleationStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            nucleation_rate_particles_per_s_um2=nucleation_rate_particles_per_s_um2,
            critical_nucleus_radius_nm=critical_nucleus_radius_nm,
            non_classical_attachment_frequency=non_classical_attachment_frequency,
            electron_beam_dose_rate_e_per_ang2_s=electron_beam_dose_rate_e_per_ang2_s,
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
    ) -> LiquidCellTemNucleationItemProfile:
        item = LiquidCellTemNucleationItemProfile(
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
    ) -> LiquidCellTemNucleationMetricTrace:
        trace = LiquidCellTemNucleationMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[LiquidCellTemNucleationStudy]:
        result = await self.session.execute(
            select(LiquidCellTemNucleationStudy)
            .options(
                selectinload(LiquidCellTemNucleationStudy.item_profiles),
                selectinload(LiquidCellTemNucleationStudy.metric_traces),
            )
            .where(LiquidCellTemNucleationStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[LiquidCellTemNucleationStudy]:
        result = await self.session.execute(
            select(LiquidCellTemNucleationStudy)
            .options(
                selectinload(LiquidCellTemNucleationStudy.item_profiles),
                selectinload(LiquidCellTemNucleationStudy.metric_traces),
            )
            .order_by(LiquidCellTemNucleationStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
