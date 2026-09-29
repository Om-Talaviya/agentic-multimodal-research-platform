"""FastAPI routes for Phase 331: Autonomous High-Throughput Ribosome Profiling (Ribo-seq) Translation Dynamics & Pause Predictor Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.riboseq_translation_dynamics_repo import RiboseqTranslationDynamicsRepository
from research.orchestration.riboseq_translation_dynamics_engine import RiboseqTranslationDynamicsEngine

router = APIRouter(prefix="/riboseq-translation-dynamics", tags=["riboseq-translation-dynamics"])


class AnalyzeRiboseqTranslationDynamicsRequest(BaseModel):
    name: str = Field(..., example="Autonomous High-Throughput Ribosome Profiling (Ribo-seq) Translation Dynamics & Pause Predictor Run 01")
    target_specimen: str = Field(default="Human Patient Cohort Sample")
    analytical_modality: str = Field(default="riboseq-translation-dynamics")
    input_scale: float = Field(default=1.0, ge=0.1, le=10.0)


@router.post("/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_and_persist(
    req: AnalyzeRiboseqTranslationDynamicsRequest,
    session: AsyncSession = Depends(get_db_session),
):
    engine = RiboseqTranslationDynamicsEngine()
    result = engine.run_analysis(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = RiboseqTranslationDynamicsRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        codon_ribosome_dwell_time_ms=result.codon_ribosome_dwell_time_ms,
        translational_efficiency_log2_fold=result.translational_efficiency_log2_fold,
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
        "codon_ribosome_dwell_time_ms": getattr(study, "codon_ribosome_dwell_time_ms"),
        "translational_efficiency_log2_fold": getattr(study, "translational_efficiency_log2_fold"),
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
    repo = RiboseqTranslationDynamicsRepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "target_specimen": s.target_specimen,
            "analytical_modality": s.analytical_modality,
            "codon_ribosome_dwell_time_ms": getattr(s, "codon_ribosome_dwell_time_ms"),
            "translational_efficiency_log2_fold": getattr(s, "translational_efficiency_log2_fold"),
            "status": s.status,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in studies
    ]
