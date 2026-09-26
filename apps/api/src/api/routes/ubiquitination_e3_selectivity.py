"""FastAPI routes for Phase 207: Proteome-Wide Ubiquitination & E3 Ligase Selectivity Engine Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.ubiquitination_e3_selectivity_repo import UbiquitinationE3SelectivityRepository
from research.proteomics.ubiquitination_e3_selectivity_engine import UbiquitinationE3SelectivityEngine

router = APIRouter(prefix="/ubiquitination-e3-selectivity", tags=["Ubiquitination E3 Selectivity"])


class AnalyzeUbiquitinationE3SelectivityRequest(BaseModel):
    name: str = Field(..., example="Proteome-Wide Ubiquitination & E3 Ligase Selectivity Engine Run 01")
    target_specimen: str = Field(default="Human Patient Cohort Sample")
    analytical_modality: str = Field(default="Ubiquitination E3 Selectivity")
    input_scale: float = Field(default=1.0, ge=0.1, le=10.0)


@router.post("/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_and_persist(
    req: AnalyzeUbiquitinationE3SelectivityRequest,
    session: AsyncSession = Depends(get_db_session),
):
    engine = UbiquitinationE3SelectivityEngine()
    result = engine.run_analysis(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = UbiquitinationE3SelectivityRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        ubiquitination_site_prediction_auroc=result.ubiquitination_site_prediction_auroc,
        e3_ligase_selectivity_binding_affinity_kd_nm=result.e3_ligase_selectivity_binding_affinity_kd_nm,
        confidence_score=result.confidence_score,
        status="completed",
        parameters={
            "composite_health_index": result.composite_health_index,
        },
        summary_report=result.summary_report,
    )

    for item in result.item_profiles:
        await repo.add_item_profile(
            study_id=study.id,
            item_name=item.item_name,
            profile_category=item.profile_category,
            quantitative_value=item.quantitative_value,
            log2_fold_change=item.log2_fold_change,
            significance_score=item.significance_score,
        )

    for trace in result.metric_traces:
        await repo.add_metric_trace(
            study_id=study.id,
            metric_dimension=trace.metric_dimension,
            observed_value=trace.observed_value,
            z_score=trace.z_score,
            p_value=trace.p_value,
        )

    return {
        "id": str(study.id),
        "name": study.name,
        "target_specimen": study.target_specimen,
        "analytical_modality": study.analytical_modality,
        "ubiquitination_site_prediction_auroc": getattr(study, "ubiquitination_site_prediction_auroc"),
        "e3_ligase_selectivity_binding_affinity_kd_nm": getattr(study, "e3_ligase_selectivity_binding_affinity_kd_nm"),
        "confidence_score": study.confidence_score,
        "item_profiles": [
            {
                "item_name": i.item_name,
                "profile_category": i.profile_category,
                "quantitative_value": i.quantitative_value,
                "log2_fold_change": i.log2_fold_change,
                "significance_score": i.significance_score,
            }
            for i in result.item_profiles
        ],
        "metric_traces": [
            {
                "metric_dimension": t.metric_dimension,
                "observed_value": t.observed_value,
                "z_score": t.z_score,
                "p_value": t.p_value,
            }
            for t in result.metric_traces
        ],
        "summary_report": study.summary_report,
    }


@router.get("/studies")
async def list_studies(
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    repo = UbiquitinationE3SelectivityRepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "target_specimen": s.target_specimen,
            "analytical_modality": s.analytical_modality,
            "ubiquitination_site_prediction_auroc": getattr(s, "ubiquitination_site_prediction_auroc"),
            "e3_ligase_selectivity_binding_affinity_kd_nm": getattr(s, "e3_ligase_selectivity_binding_affinity_kd_nm"),
            "status": s.status,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in studies
    ]
