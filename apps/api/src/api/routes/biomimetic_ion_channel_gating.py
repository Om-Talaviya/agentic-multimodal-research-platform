"""FastAPI routes for Phase 318: Autonomous Artificial Biomimetic Solid-State Nanopore Ion-Channel Gating & Selectivity Predictor Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.biomimetic_ion_channel_gating_repo import BiomimeticIonChannelGatingRepository
from research.orchestration.biomimetic_ion_channel_gating_engine import BiomimeticIonChannelGatingEngine

router = APIRouter(prefix="/biomimetic-ion-channel-gating", tags=["biomimetic-ion-channel-gating"])


class AnalyzeBiomimeticIonChannelGatingRequest(BaseModel):
    name: str = Field(..., example="Autonomous Artificial Biomimetic Solid-State Nanopore Ion-Channel Gating & Selectivity Predictor Run 01")
    target_specimen: str = Field(default="Human Patient Cohort Sample")
    analytical_modality: str = Field(default="biomimetic-ion-channel-gating")
    input_scale: float = Field(default=1.0, ge=0.1, le=10.0)


@router.post("/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_and_persist(
    req: AnalyzeBiomimeticIonChannelGatingRequest,
    session: AsyncSession = Depends(get_db_session),
):
    engine = BiomimeticIonChannelGatingEngine()
    result = engine.run_analysis(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = BiomimeticIonChannelGatingRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        potassium_over_sodium_selectivity_ratio=result.potassium_over_sodium_selectivity_ratio,
        single_channel_conductance_pico_siemens=result.single_channel_conductance_pico_siemens,
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
        "potassium_over_sodium_selectivity_ratio": getattr(study, "potassium_over_sodium_selectivity_ratio"),
        "single_channel_conductance_pico_siemens": getattr(study, "single_channel_conductance_pico_siemens"),
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
    repo = BiomimeticIonChannelGatingRepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "target_specimen": s.target_specimen,
            "analytical_modality": s.analytical_modality,
            "potassium_over_sodium_selectivity_ratio": getattr(s, "potassium_over_sodium_selectivity_ratio"),
            "single_channel_conductance_pico_siemens": getattr(s, "single_channel_conductance_pico_siemens"),
            "status": s.status,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in studies
    ]
