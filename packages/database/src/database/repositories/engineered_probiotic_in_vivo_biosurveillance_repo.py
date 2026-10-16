"""Repository for Phase 574: Autonomous Engineered Probiotic Gastrointestinal In-Vivo Biosurveillance & Colitis Biomarker Logic Gate Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.engineered_probiotic_in_vivo_biosurveillance import (
    EngineeredProbioticInVivoBiosurveillanceStudy,
    EngineeredProbioticInVivoBiosurveillanceItemProfile,
    EngineeredProbioticInVivoBiosurveillanceMetricTrace,
)


class EngineeredProbioticInVivoBiosurveillanceRepository:
    """Repository for Autonomous Engineered Probiotic Gastrointestinal In-Vivo Biosurveillance & Colitis Biomarker Logic Gate Engine storage and retrieval."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str,
        analytical_modality: str,
        calprotectin_induction_fold_change: float,
        genetic_circuit_retention_stability: float,
        gut_colonization_density_cfu_g: float,
        false_positive_activation_rate: float,
        confidence_score: float = 0.996,
        status: str = "completed",
        summary_report: Optional[str] = None,
        parameters: Optional[dict] = None,
    ) -> EngineeredProbioticInVivoBiosurveillanceStudy:
        study = EngineeredProbioticInVivoBiosurveillanceStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            calprotectin_induction_fold_change=calprotectin_induction_fold_change,
            genetic_circuit_retention_stability=genetic_circuit_retention_stability,
            gut_colonization_density_cfu_g=gut_colonization_density_cfu_g,
            false_positive_activation_rate=false_positive_activation_rate,
            confidence_score=confidence_score,
            status=status,
            summary_report=summary_report,
            parameters=parameters or {},
        )
        self.session.add(study)
        await self.session.commit()
        await self.session.refresh(study)
        return study

    async def get_study(self, study_id: UUID) -> Optional[EngineeredProbioticInVivoBiosurveillanceStudy]:
        stmt = select(EngineeredProbioticInVivoBiosurveillanceStudy).where(EngineeredProbioticInVivoBiosurveillanceStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[EngineeredProbioticInVivoBiosurveillanceStudy]:
        stmt = select(EngineeredProbioticInVivoBiosurveillanceStudy).order_by(EngineeredProbioticInVivoBiosurveillanceStudy.created_at.desc()).limit(limit)
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
    ) -> EngineeredProbioticInVivoBiosurveillanceItemProfile:
        profile = EngineeredProbioticInVivoBiosurveillanceItemProfile(
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
    ) -> EngineeredProbioticInVivoBiosurveillanceMetricTrace:
        trace = EngineeredProbioticInVivoBiosurveillanceMetricTrace(
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
