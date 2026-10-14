"""Repository for Phase 485: Autonomous Bacterial Quorum Quenching Enzymatic Lactonase Biofilm Dispersion Forecaster."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.quorum_quenching_lactonase_dispersion import (
    QuorumQuenchingLactonaseDispersionStudy,
    QuorumQuenchingLactonaseDispersionItemProfile,
    QuorumQuenchingLactonaseDispersionMetricTrace,
)


class QuorumQuenchingLactonaseDispersionRepository:
    """Database operations for Autonomous Bacterial Quorum Quenching Enzymatic Lactonase Biofilm Dispersion Forecaster."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Pseudomonas aeruginosa PAO1 Mature Biofilm with Immobilized Phosphotriesterase-Like Lactonase (PLL)",
        analytical_modality: str = "quorum-quenching-lactonase",
        ahl_hydrolysis_kcat_over_km_M_inv_s_inv: float = 280000.0,
        biofilm_extracellular_matrix_reduction_pct: float = 78.5,
        quorum_regulated_pyocyanin_suppression_pct: float = 92.4,
        antibiotic_potency_synergy_fold_increase: float = 6.4,
        confidence_score: float = 0.988,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> QuorumQuenchingLactonaseDispersionStudy:
        study = QuorumQuenchingLactonaseDispersionStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            ahl_hydrolysis_kcat_over_km_M_inv_s_inv=ahl_hydrolysis_kcat_over_km_M_inv_s_inv,
            biofilm_extracellular_matrix_reduction_pct=biofilm_extracellular_matrix_reduction_pct,
            quorum_regulated_pyocyanin_suppression_pct=quorum_regulated_pyocyanin_suppression_pct,
            antibiotic_potency_synergy_fold_increase=antibiotic_potency_synergy_fold_increase,
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
    ) -> QuorumQuenchingLactonaseDispersionItemProfile:
        item = QuorumQuenchingLactonaseDispersionItemProfile(
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
    ) -> QuorumQuenchingLactonaseDispersionMetricTrace:
        trace = QuorumQuenchingLactonaseDispersionMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[QuorumQuenchingLactonaseDispersionStudy]:
        result = await self.session.execute(
            select(QuorumQuenchingLactonaseDispersionStudy)
            .options(
                selectinload(QuorumQuenchingLactonaseDispersionStudy.item_profiles),
                selectinload(QuorumQuenchingLactonaseDispersionStudy.metric_traces),
            )
            .where(QuorumQuenchingLactonaseDispersionStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[QuorumQuenchingLactonaseDispersionStudy]:
        result = await self.session.execute(
            select(QuorumQuenchingLactonaseDispersionStudy)
            .options(
                selectinload(QuorumQuenchingLactonaseDispersionStudy.item_profiles),
                selectinload(QuorumQuenchingLactonaseDispersionStudy.metric_traces),
            )
            .order_by(QuorumQuenchingLactonaseDispersionStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
