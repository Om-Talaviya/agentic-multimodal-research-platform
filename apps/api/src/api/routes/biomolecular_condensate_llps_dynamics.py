"""FastAPI routes for Phase 258: Autonomous Liquid-Liquid Phase Separation (LLPS) Biomolecular Condensate Multivalent Driving Force Engine Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.biomolecular_condensate_llps_dynamics_repo import BiomolecularCondensateLlpsDynamicsRepository
from research.orchestration.biomolecular_condensate_llps_dynamics_engine import BiomolecularCondensateLlpsDynamicsEngine

router = APIRouter(prefix="/biomolecular-condensate-llps-dynamics", tags=["biomolecular-condensate-llps-dynamics"])


class AnalyzeBiomolecularCondensateLlpsDynamicsRequest(BaseModel):
    name: str = Field(..., example="Autonomous Liquid-Liquid Phase Separation (LLPS) Biomolecular Condensate Multivalent Driving Force Engine Run 01")
    target_specimen: str = Field(default="Human Patient Cohort Sample")
    analytical_modality: str = Field(default="biomolecular-condensate-llps-dynamics")
    input_scale: float = Field(default=1.0, ge=0.1, le=10.0)


@router.post("/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_and_persist(
    req: AnalyzeBiomolecularCondensateLlpsDynamicsRequest,
    session: AsyncSession = Depends(get_db_session),
):
    engine = BiomolecularCondensateLlpsDynamicsEngine()
    result = engine.run_analysis(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = BiomolecularCondensateLlpsDynamicsRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        critical_saturation_concentration_csat_uM=result.critical_saturation_concentration_csat_uM,
        flory_huggins_interaction_chi_parameter=result.flory_huggins_interaction_chi_parameter,
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
        "critical_saturation_concentration_csat_uM": getattr(study, "critical_saturation_concentration_csat_uM"),
        "flory_huggins_interaction_chi_parameter": getattr(study, "flory_huggins_interaction_chi_parameter"),
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
    repo = BiomolecularCondensateLlpsDynamicsRepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "target_specimen": s.target_specimen,
            "analytical_modality": s.analytical_modality,
            "critical_saturation_concentration_csat_uM": getattr(s, "critical_saturation_concentration_csat_uM"),
            "flory_huggins_interaction_chi_parameter": getattr(s, "flory_huggins_interaction_chi_parameter"),
            "status": s.status,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in studies
    ]
