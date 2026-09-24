"""Repository for Milestone v1.9 Pan-Cancer Stratification (Phase 161)."""

import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.milestone_v1_9 import (
    DBMilestoneV19Orchestration,
    DBPanCancerPatientStratificationCluster,
    DBCrossModalTherapeuticEfficacyMatrix,
)


class MilestoneV19Repository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_orchestration(
        self,
        cohort_study_name: str,
        milestone_version: str,
        total_phases_integrated: int,
        patient_cohort_size: int,
        clusters_identified_count: int,
        mean_hazard_ratio_separation: float,
        global_cross_modal_concordance: float,
    ) -> DBMilestoneV19Orchestration:
        orch = DBMilestoneV19Orchestration(
            id=uuid.uuid4(),
            cohort_study_name=cohort_study_name,
            milestone_version=milestone_version,
            total_phases_integrated=total_phases_integrated,
            patient_cohort_size=patient_cohort_size,
            clusters_identified_count=clusters_identified_count,
            mean_hazard_ratio_separation=mean_hazard_ratio_separation,
            global_cross_modal_concordance=global_cross_modal_concordance,
        )
        self.db.add(orch)
        await self.db.commit()
        await self.db.refresh(orch)
        return orch

    async def add_cluster(
        self,
        orchestration_id: uuid.UUID,
        cluster_index: int,
        subtype_designation: str,
        dominant_pathway_alteration: str,
        patient_percentage: float,
        median_progression_free_survival_months: float,
        recommended_therapy: str,
    ) -> DBPanCancerPatientStratificationCluster:
        rec = DBPanCancerPatientStratificationCluster(
            id=uuid.uuid4(),
            orchestration_id=orchestration_id,
            cluster_index=cluster_index,
            subtype_designation=subtype_designation,
            dominant_pathway_alteration=dominant_pathway_alteration,
            patient_percentage=patient_percentage,
            median_progression_free_survival_months=median_progression_free_survival_months,
            recommended_therapy=recommended_therapy,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def add_efficacy_matrix(
        self,
        orchestration_id: uuid.UUID,
        therapeutic_agent: str,
        target_subtype: str,
        predicted_response_rate_pct: float,
        synergy_combination_score: float,
    ) -> DBCrossModalTherapeuticEfficacyMatrix:
        rec = DBCrossModalTherapeuticEfficacyMatrix(
            id=uuid.uuid4(),
            orchestration_id=orchestration_id,
            therapeutic_agent=therapeutic_agent,
            target_subtype=target_subtype,
            predicted_response_rate_pct=predicted_response_rate_pct,
            synergy_combination_score=synergy_combination_score,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def get_orchestration_with_details(self, orchestration_id: uuid.UUID) -> Optional[DBMilestoneV19Orchestration]:
        stmt = (
            select(DBMilestoneV19Orchestration)
            .where(DBMilestoneV19Orchestration.id == orchestration_id)
            .options(
                selectinload(DBMilestoneV19Orchestration.clusters),
                selectinload(DBMilestoneV19Orchestration.efficacy_matrix),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
