"""FastAPI routes for Phase 289: Autonomous Spatial Multi-Omics Whole-Transcriptome In-Situ Sequencing (ISS) Padlock Decoding Engine Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.iss_padlock_rolling_circle_repo import IssPadlockRollingCircleRepository
from research.orchestration.iss_padlock_rolling_circle_engine import IssPadlockRollingCircleEngine

router = APIRouter(prefix="/iss-padlock-rolling-circle", tags=["iss-padlock-rolling-circle"])


class AnalyzeIssPadlockRollingCircleRequest(BaseModel):
    name: str = Field(..., example="Autonomous Spatial Multi-Omics Whole-Transcriptome In-Situ Sequencing (ISS) Padlock Decoding Engine Run 01")
    target_specimen: str = Field(default="Human Patient Cohort Sample")
    analytical_modality: str = Field(default="iss-padlock-rolling-circle")
    input_scale: float = Field(default=1.0, ge=0.1, le=10.0)


@router.post("/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_and_persist(
    req: AnalyzeIssPadlockRollingCircleRequest,
    session: AsyncSession = Depends(get_db_session),
):
    engine = IssPadlockRollingCircleEngine()
    result = engine.run_analysis(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = IssPadlockRollingCircleRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        optical_decoding_accuracy_pct=result.optical_decoding_accuracy_pct,
        subcellular_rca_puncta_density_per_100um2=result.subcellular_rca_puncta_density_per_100um2,
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
        "optical_decoding_accuracy_pct": getattr(study, "optical_decoding_accuracy_pct"),
        "subcellular_rca_puncta_density_per_100um2": getattr(study, "subcellular_rca_puncta_density_per_100um2"),
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
    repo = IssPadlockRollingCircleRepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "target_specimen": s.target_specimen,
            "analytical_modality": s.analytical_modality,
            "optical_decoding_accuracy_pct": getattr(s, "optical_decoding_accuracy_pct"),
            "subcellular_rca_puncta_density_per_100um2": getattr(s, "subcellular_rca_puncta_density_per_100um2"),
            "status": s.status,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in studies
    ]
