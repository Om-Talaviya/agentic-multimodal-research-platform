"""Repository for Phase 344: Autonomous Lipid Nanoparticle (LNP) In Vivo Endosomal Escape & Cytosolic Release Efficiency Predictor."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.lnp_endosomal_escape_predictor import (
    LnpEndosomalEscapePredictorStudy,
    LnpEndosomalEscapePredictorItemProfile,
    LnpEndosomalEscapePredictorMetricTrace,
)


class LnpEndosomalEscapePredictorRepository:
    """Database operations for Autonomous Lipid Nanoparticle (LNP) In Vivo Endosomal Escape & Cytosolic Release Efficiency Predictor studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "lnp-endosomal-escape",
        endosomal_escape_fractional_efficiency_pct: float = 8.4,
        cytosolic_mrna_translation_half_life_hr: float = 28.5,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> LnpEndosomalEscapePredictorStudy:
        study = LnpEndosomalEscapePredictorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            endosomal_escape_fractional_efficiency_pct=endosomal_escape_fractional_efficiency_pct,
            cytosolic_mrna_translation_half_life_hr=cytosolic_mrna_translation_half_life_hr,
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
        profile_category: str = "Primary Target",
        quantitative_value: float = 100.0,
        log2_fold_change: float = 1.5,
        significance_score: float = 0.95,
    ) -> LnpEndosomalEscapePredictorItemProfile:
        item = LnpEndosomalEscapePredictorItemProfile(
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
        z_score: float = 2.1,
        p_value: float = 0.001,
    ) -> LnpEndosomalEscapePredictorMetricTrace:
        item = LnpEndosomalEscapePredictorMetricTrace(
            study_id=study_id,
            metric_dimension=metric_dimension,
            observed_value=observed_value,
            z_score=z_score,
            p_value=p_value,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_study(self, study_id: UUID) -> Optional[LnpEndosomalEscapePredictorStudy]:
        stmt = select(LnpEndosomalEscapePredictorStudy).where(LnpEndosomalEscapePredictorStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[LnpEndosomalEscapePredictorStudy]:
        stmt = select(LnpEndosomalEscapePredictorStudy).order_by(LnpEndosomalEscapePredictorStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
