"""Repository for Phase 207: Proteome-Wide Ubiquitination & E3 Ligase Selectivity Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.ubiquitination_e3_selectivity import (
    UbiquitinationE3SelectivityStudy,
    UbiquitinationE3SelectivityItemProfile,
    UbiquitinationE3SelectivityMetricTrace,
)


class UbiquitinationE3SelectivityRepository:
    """Database operations for Proteome-Wide Ubiquitination & E3 Ligase Selectivity Engine studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "Ubiquitination E3 Selectivity",
        ubiquitination_site_prediction_auroc: float = 0.948,
        e3_ligase_selectivity_binding_affinity_kd_nm: float = 24.5,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> UbiquitinationE3SelectivityStudy:
        study = UbiquitinationE3SelectivityStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            ubiquitination_site_prediction_auroc=ubiquitination_site_prediction_auroc,
            e3_ligase_selectivity_binding_affinity_kd_nm=e3_ligase_selectivity_binding_affinity_kd_nm,
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
    ) -> UbiquitinationE3SelectivityItemProfile:
        item = UbiquitinationE3SelectivityItemProfile(
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
    ) -> UbiquitinationE3SelectivityMetricTrace:
        item = UbiquitinationE3SelectivityMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[UbiquitinationE3SelectivityStudy]:
        stmt = select(UbiquitinationE3SelectivityStudy).where(UbiquitinationE3SelectivityStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[UbiquitinationE3SelectivityStudy]:
        stmt = select(UbiquitinationE3SelectivityStudy).order_by(UbiquitinationE3SelectivityStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
