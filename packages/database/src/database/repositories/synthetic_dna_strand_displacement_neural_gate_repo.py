"""Repository for Phase 570: Autonomous Synthetic DNA Strand Displacement (DSD) Molecular Neural Network Winner-Take-All Classifier Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.synthetic_dna_strand_displacement_neural_gate import (
    SyntheticDnaStrandDisplacementNeuralGateStudy,
    SyntheticDnaStrandDisplacementNeuralGateItemProfile,
    SyntheticDnaStrandDisplacementNeuralGateMetricTrace,
)


class SyntheticDnaStrandDisplacementNeuralGateRepository:
    """Repository for Autonomous Synthetic DNA Strand Displacement (DSD) Molecular Neural Network Winner-Take-All Classifier Engine storage and retrieval."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str,
        analytical_modality: str,
        toehold_exchange_rate_constant_m_s: float,
        signal_to_leakage_ratio: float,
        winner_take_all_convergence_time_s: float,
        decision_boundary_sharpness: float,
        confidence_score: float = 0.997,
        status: str = "completed",
        summary_report: Optional[str] = None,
        parameters: Optional[dict] = None,
    ) -> SyntheticDnaStrandDisplacementNeuralGateStudy:
        study = SyntheticDnaStrandDisplacementNeuralGateStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            toehold_exchange_rate_constant_m_s=toehold_exchange_rate_constant_m_s,
            signal_to_leakage_ratio=signal_to_leakage_ratio,
            winner_take_all_convergence_time_s=winner_take_all_convergence_time_s,
            decision_boundary_sharpness=decision_boundary_sharpness,
            confidence_score=confidence_score,
            status=status,
            summary_report=summary_report,
            parameters=parameters or {},
        )
        self.session.add(study)
        await self.session.commit()
        await self.session.refresh(study)
        return study

    async def get_study(self, study_id: UUID) -> Optional[SyntheticDnaStrandDisplacementNeuralGateStudy]:
        stmt = select(SyntheticDnaStrandDisplacementNeuralGateStudy).where(SyntheticDnaStrandDisplacementNeuralGateStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[SyntheticDnaStrandDisplacementNeuralGateStudy]:
        stmt = select(SyntheticDnaStrandDisplacementNeuralGateStudy).order_by(SyntheticDnaStrandDisplacementNeuralGateStudy.created_at.desc()).limit(limit)
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
    ) -> SyntheticDnaStrandDisplacementNeuralGateItemProfile:
        profile = SyntheticDnaStrandDisplacementNeuralGateItemProfile(
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
    ) -> SyntheticDnaStrandDisplacementNeuralGateMetricTrace:
        trace = SyntheticDnaStrandDisplacementNeuralGateMetricTrace(
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
