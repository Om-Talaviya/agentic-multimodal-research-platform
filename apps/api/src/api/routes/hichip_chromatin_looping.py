"""FastAPI routes for Phase 200: Epigenomic Hi-ChIP & Enhancer-Promoter Chromatin Looping Engine Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.hichip_chromatin_looping_repo import HiChIPChromatinLoopingRepository
from research.genomics.hichip_chromatin_looping_engine import HiChIPChromatinLoopingEngine

router = APIRouter(prefix="/hichip-chromatin-looping", tags=["Hi-ChIP Chromatin Looping"])


class AnalyzeHiChIPChromatinLoopingRequest(BaseModel):
    name: str = Field(..., example="Epigenomic Hi-ChIP & Enhancer-Promoter Chromatin Looping Engine Run 01")
    target_specimen: str = Field(default="Human Patient Cohort Sample")
    analytical_modality: str = Field(default="Hi-ChIP Chromatin Looping")
    input_scale: float = Field(default=1.0, ge=0.1, le=10.0)


@router.post("/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_and_persist(
    req: AnalyzeHiChIPChromatinLoopingRequest,
    session: AsyncSession = Depends(get_db_session),
):
    engine = HiChIPChromatinLoopingEngine()
    result = engine.run_analysis(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = HiChIPChromatinLoopingRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        loop_contact_enrichment_score=result.loop_contact_enrichment_score,
        enhancer_promoter_interaction_strength=result.enhancer_promoter_interaction_strength,
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
        "loop_contact_enrichment_score": getattr(study, "loop_contact_enrichment_score"),
        "enhancer_promoter_interaction_strength": getattr(study, "enhancer_promoter_interaction_strength"),
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
    repo = HiChIPChromatinLoopingRepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "target_specimen": s.target_specimen,
            "analytical_modality": s.analytical_modality,
            "loop_contact_enrichment_score": getattr(s, "loop_contact_enrichment_score"),
            "enhancer_promoter_interaction_strength": getattr(s, "enhancer_promoter_interaction_strength"),
            "status": s.status,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in studies
    ]
