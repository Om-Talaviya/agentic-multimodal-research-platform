"""Repository for Phase 286: Autonomous Multi-Organ Pharmacometabolomics Drug Interaction & Cytochrome P450 Metabolic Clearance Simulator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cyp450_pharmacometabolomics_clearance import (
    Cyp450PharmacometabolomicsClearanceStudy,
    Cyp450PharmacometabolomicsClearanceItemProfile,
    Cyp450PharmacometabolomicsClearanceMetricTrace,
)


class Cyp450PharmacometabolomicsClearanceRepository:
    """Database operations for Autonomous Multi-Organ Pharmacometabolomics Drug Interaction & Cytochrome P450 Metabolic Clearance Simulator studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "cyp450-pharmacometabolomics-clearance",
        cyp_intrinsic_clearance_prediction_accuracy: float = 96.5,
        drug_drug_interaction_auc_ratio_error_pct: float = 8.4,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> Cyp450PharmacometabolomicsClearanceStudy:
        study = Cyp450PharmacometabolomicsClearanceStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            cyp_intrinsic_clearance_prediction_accuracy=cyp_intrinsic_clearance_prediction_accuracy,
            drug_drug_interaction_auc_ratio_error_pct=drug_drug_interaction_auc_ratio_error_pct,
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
    ) -> Cyp450PharmacometabolomicsClearanceItemProfile:
        item = Cyp450PharmacometabolomicsClearanceItemProfile(
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
    ) -> Cyp450PharmacometabolomicsClearanceMetricTrace:
        item = Cyp450PharmacometabolomicsClearanceMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[Cyp450PharmacometabolomicsClearanceStudy]:
        stmt = select(Cyp450PharmacometabolomicsClearanceStudy).where(Cyp450PharmacometabolomicsClearanceStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[Cyp450PharmacometabolomicsClearanceStudy]:
        stmt = select(Cyp450PharmacometabolomicsClearanceStudy).order_by(Cyp450PharmacometabolomicsClearanceStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
