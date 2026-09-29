"""Repository for Phase 293: Autonomous Non-Viral Lipid Nanoparticle (LNP) Endosomal Escape Kinetics & Bioavailability Forecaster."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.lnp_endosomal_escape_kinetics import (
    LnpEndosomalEscapeKineticsStudy,
    LnpEndosomalEscapeKineticsItemProfile,
    LnpEndosomalEscapeKineticsMetricTrace,
)


class LnpEndosomalEscapeKineticsRepository:
    """Database operations for Autonomous Non-Viral Lipid Nanoparticle (LNP) Endosomal Escape Kinetics & Bioavailability Forecaster studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "lnp-endosomal-escape-kinetics",
        cytosolic_payload_escape_efficiency_pct: float = 14.8,
        endosomal_rupture_half_time_minutes: float = 35.0,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> LnpEndosomalEscapeKineticsStudy:
        study = LnpEndosomalEscapeKineticsStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            cytosolic_payload_escape_efficiency_pct=cytosolic_payload_escape_efficiency_pct,
            endosomal_rupture_half_time_minutes=endosomal_rupture_half_time_minutes,
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
    ) -> LnpEndosomalEscapeKineticsItemProfile:
        item = LnpEndosomalEscapeKineticsItemProfile(
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
    ) -> LnpEndosomalEscapeKineticsMetricTrace:
        item = LnpEndosomalEscapeKineticsMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[LnpEndosomalEscapeKineticsStudy]:
        stmt = select(LnpEndosomalEscapeKineticsStudy).where(LnpEndosomalEscapeKineticsStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[LnpEndosomalEscapeKineticsStudy]:
        stmt = select(LnpEndosomalEscapeKineticsStudy).order_by(LnpEndosomalEscapeKineticsStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
