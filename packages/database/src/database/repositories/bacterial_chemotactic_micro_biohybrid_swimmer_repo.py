"""Repository for Phase 568: Autonomous Engineered Bacterial Chemotactic Micro-Biohybrid Swimmer Targeted Navigation & Tumble-Run Kinetics Simulator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.bacterial_chemotactic_micro_biohybrid_swimmer import (
    BacterialChemotacticMicroBiohybridSwimmerStudy,
    BacterialChemotacticMicroBiohybridSwimmerItemProfile,
    BacterialChemotacticMicroBiohybridSwimmerMetricTrace,
)


class BacterialChemotacticMicroBiohybridSwimmerRepository:
    """Repository for Autonomous Engineered Bacterial Chemotactic Micro-Biohybrid Swimmer Targeted Navigation & Tumble-Run Kinetics Simulator storage and retrieval."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str,
        analytical_modality: str,
        chemotactic_drift_velocity_um_s: float,
        run_tumble_frequency_ratio: float,
        target_accumulation_index: float,
        flagellar_motor_torque_efficiency: float,
        confidence_score: float = 0.995,
        status: str = "completed",
        summary_report: Optional[str] = None,
        parameters: Optional[dict] = None,
    ) -> BacterialChemotacticMicroBiohybridSwimmerStudy:
        study = BacterialChemotacticMicroBiohybridSwimmerStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            chemotactic_drift_velocity_um_s=chemotactic_drift_velocity_um_s,
            run_tumble_frequency_ratio=run_tumble_frequency_ratio,
            target_accumulation_index=target_accumulation_index,
            flagellar_motor_torque_efficiency=flagellar_motor_torque_efficiency,
            confidence_score=confidence_score,
            status=status,
            summary_report=summary_report,
            parameters=parameters or {},
        )
        self.session.add(study)
        await self.session.commit()
        await self.session.refresh(study)
        return study

    async def get_study(self, study_id: UUID) -> Optional[BacterialChemotacticMicroBiohybridSwimmerStudy]:
        stmt = select(BacterialChemotacticMicroBiohybridSwimmerStudy).where(BacterialChemotacticMicroBiohybridSwimmerStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[BacterialChemotacticMicroBiohybridSwimmerStudy]:
        stmt = select(BacterialChemotacticMicroBiohybridSwimmerStudy).order_by(BacterialChemotacticMicroBiohybridSwimmerStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_item_profile(
        self,
        study_id: UUID,
        item_name: str,
        quantitative_value: float,
        profile_category: str = "Analysis Profile",
        log2_fold_change: float = 1.5,
        significance_score: float = 0.95,
    ) -> BacterialChemotacticMicroBiohybridSwimmerItemProfile:
        profile = BacterialChemotacticMicroBiohybridSwimmerItemProfile(
            study_id=study_id,
            item_name=item_name,
            profile_category=profile_category,
            quantitative_value=quantitative_value,
            log2_fold_change=log2_fold_change,
            significance_score=significance_score,
        )
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def add_metric_trace(
        self,
        study_id: UUID,
        metric_dimension: str,
        observed_value: float,
        z_score: float = 0.0,
        p_value: float = 0.05,
    ) -> BacterialChemotacticMicroBiohybridSwimmerMetricTrace:
        trace = BacterialChemotacticMicroBiohybridSwimmerMetricTrace(
            study_id=study_id,
            metric_dimension=metric_dimension,
            observed_value=observed_value,
            z_score=z_score,
            p_value=p_value,
        )
        self.session.add(trace)
        await self.session.commit()
        await self.session.refresh(trace)
        return trace
