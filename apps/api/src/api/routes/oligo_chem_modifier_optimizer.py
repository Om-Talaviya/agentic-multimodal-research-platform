"""FastAPI routes for Phase 349: Autonomous Therapeutic Oligonucleotide Chemical Modification (PS/2-MOE/LNA) Stability & Affinity Optimizer Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.oligo_chem_modifier_optimizer_repo import OligoChemModifierOptimizerRepository
from research.orchestration.oligo_chem_modifier_optimizer_engine import OligoChemModifierOptimizerEngine

router = APIRouter(prefix="/oligo-chem-modifier", tags=["oligo-chem-modifier"])


class AnalyzeOligoChemModifierOptimizerRequest(BaseModel):
    name: str = Field(..., example="Autonomous Therapeutic Oligonucleotide Chemical Modification (PS/2-MOE/LNA) Stability & Affinity Optimizer Run 01")
    target_specimen: str = Field(default="Human Patient Cohort Sample")
    analytical_modality: str = Field(default="oligo-chem-modifier")
    input_scale: float = Field(default=1.0, ge=0.1, le=10.0)


@router.post("/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_and_persist(
    req: AnalyzeOligoChemModifierOptimizerRequest,
    session: AsyncSession = Depends(get_db_session),
):
    engine = OligoChemModifierOptimizerEngine()
    result = engine.run_analysis(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = OligoChemModifierOptimizerRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        duplex_thermal_stability_delta_tm_per_mod_celsius=result.duplex_thermal_stability_delta_tm_per_mod_celsius,
        serum_exonuclease_resistance_half_life_hr=result.serum_exonuclease_resistance_half_life_hr,
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
        "duplex_thermal_stability_delta_tm_per_mod_celsius": getattr(study, "duplex_thermal_stability_delta_tm_per_mod_celsius"),
        "serum_exonuclease_resistance_half_life_hr": getattr(study, "serum_exonuclease_resistance_half_life_hr"),
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
    repo = OligoChemModifierOptimizerRepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "target_specimen": s.target_specimen,
            "analytical_modality": s.analytical_modality,
            "duplex_thermal_stability_delta_tm_per_mod_celsius": getattr(s, "duplex_thermal_stability_delta_tm_per_mod_celsius"),
            "serum_exonuclease_resistance_half_life_hr": getattr(s, "serum_exonuclease_resistance_half_life_hr"),
            "status": s.status,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in studies
    ]
