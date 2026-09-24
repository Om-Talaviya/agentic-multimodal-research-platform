"""FastAPI Route for Milestone v1.9 Pan-Cancer Stratification (Phase 161)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.milestone_v1_9_repo import MilestoneV19Repository
from research.orchestration.milestone_v1_9_engine import (
    MilestoneV19SynthesisEngine,
    MilestoneV19StratificationRequest,
    MilestoneV19StratificationResult,
)

router = APIRouter(prefix="/milestone-v1-9", tags=["Milestone v1.9 Pan-Cancer Stratification"])


@router.post("/stratify", response_model=MilestoneV19StratificationResult)
async def stratify_cohort(
    payload: MilestoneV19StratificationRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = MilestoneV19SynthesisEngine()
    result = engine.stratify_cohort(payload)

    repo = MilestoneV19Repository(db)
    orch = await repo.create_orchestration(
        cohort_study_name=result.cohort_study_name,
        milestone_version=result.milestone_version,
        total_phases_integrated=result.total_phases_integrated,
        patient_cohort_size=result.patient_cohort_size,
        clusters_identified_count=result.clusters_identified_count,
        mean_hazard_ratio_separation=result.mean_hazard_ratio_separation,
        global_cross_modal_concordance=result.global_cross_modal_concordance,
    )

    for c in result.clusters:
        await repo.add_cluster(
            orchestration_id=orch.id,
            cluster_index=c.cluster_index,
            subtype_designation=c.subtype_designation,
            dominant_pathway_alteration=c.dominant_pathway_alteration,
            patient_percentage=c.patient_percentage,
            median_progression_free_survival_months=c.median_progression_free_survival_months,
            recommended_therapy=c.recommended_therapy,
        )

    for m in result.efficacy_matrix:
        await repo.add_efficacy_matrix(
            orchestration_id=orch.id,
            therapeutic_agent=m.therapeutic_agent,
            target_subtype=m.target_subtype,
            predicted_response_rate_pct=m.predicted_response_rate_pct,
            synergy_combination_score=m.synergy_combination_score,
        )

    return result
