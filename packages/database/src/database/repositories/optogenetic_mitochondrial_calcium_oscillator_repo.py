"""Repository for Phase 531: Autonomous Spatially-Resolved Optogenetic Mitochondrial Calcium Spark & Bioenergetics Modeler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.optogenetic_mitochondrial_calcium_oscillator import (
    OptogeneticMitochondrialCalciumOscillatorStudy,
    OptogeneticMitochondrialCalciumOscillatorItemProfile,
    OptogeneticMitochondrialCalciumOscillatorMetricTrace,
)


class OptogeneticMitochondrialCalciumOscillatorRepository:
    """Database operations for Autonomous Spatially-Resolved Optogenetic Mitochondrial Calcium Spark & Bioenergetics Modeler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Cardiomyocyte Syncytium with Mitochondrially-Targeted ChR2 and R-GECO1 Probes",
        analytical_modality: str = "optogenetic-mitochondrial-calcium",
        matrix_calcium_influx_rate_uM_per_s: float = 12.4,
        mcu_channel_open_probability: float = 0.84,
        atp_production_coupling_gain_pct: float = 28.5,
        mptp_opening_prevention_threshold_uM: float = 4.2,
        confidence_score: float = 0.993,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> OptogeneticMitochondrialCalciumOscillatorStudy:
        study = OptogeneticMitochondrialCalciumOscillatorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            matrix_calcium_influx_rate_uM_per_s=matrix_calcium_influx_rate_uM_per_s,
            mcu_channel_open_probability=mcu_channel_open_probability,
            atp_production_coupling_gain_pct=atp_production_coupling_gain_pct,
            mptp_opening_prevention_threshold_uM=mptp_opening_prevention_threshold_uM,
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
    ) -> OptogeneticMitochondrialCalciumOscillatorItemProfile:
        item = OptogeneticMitochondrialCalciumOscillatorItemProfile(
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
    ) -> OptogeneticMitochondrialCalciumOscillatorMetricTrace:
        trace = OptogeneticMitochondrialCalciumOscillatorMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[OptogeneticMitochondrialCalciumOscillatorStudy]:
        stmt = (
            select(OptogeneticMitochondrialCalciumOscillatorStudy)
            .where(OptogeneticMitochondrialCalciumOscillatorStudy.id == study_id)
            .options(
                selectinload(OptogeneticMitochondrialCalciumOscillatorStudy.item_profiles),
                selectinload(OptogeneticMitochondrialCalciumOscillatorStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[OptogeneticMitochondrialCalciumOscillatorStudy]:
        stmt = (
            select(OptogeneticMitochondrialCalciumOscillatorStudy)
            .order_by(OptogeneticMitochondrialCalciumOscillatorStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(OptogeneticMitochondrialCalciumOscillatorStudy.item_profiles),
                selectinload(OptogeneticMitochondrialCalciumOscillatorStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
