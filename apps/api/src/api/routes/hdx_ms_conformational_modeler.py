"""FastAPI routes for Phase 380: Autonomous Proteome-Wide Hydrogen-Deuterium Exchange Mass Spectrometry (HDX-MS) Conformational State Modeler Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.hdx_ms_conformational_modeler_repo import HdxMsConformationalModelerRepository
from research.orchestration.hdx_ms_conformational_modeler_engine import HdxMsConformationalModelerEngine

router = APIRouter(prefix="/hdx-ms-conformational-modeler", tags=["hdx-ms-conformational-modeler"])


class AnalyzeHdxMsConformationalModelerRequest(BaseModel):
    name: str = Field(..., example="Autonomous Proteome-Wide Hydrogen-Deuterium Exchange Mass Spectrometry (HDX-MS) Conformational State Modeler Run 01")
    target_specimen: str = Field(default="Human Patient Cohort Sample")
    analytical_modality: str = Field(default="hdx-ms-conformational-modeler")
    input_scale: float = Field(default=1.0, ge=0.1, le=10.0)


@router.post("/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_and_persist(
    req: AnalyzeHdxMsConformationalModelerRequest,
    session: AsyncSession = Depends(get_db_session),
):
    engine = HdxMsConformationalModelerEngine()
    result = engine.run_analysis(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = HdxMsConformationalModelerRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        hdx_peptic_peptide_sequence_coverage_pct=result.hdx_peptic_peptide_sequence_coverage_pct,
        deuterium_incorporation_mass_accuracy_ppm=result.deuterium_incorporation_mass_accuracy_ppm,
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
        "hdx_peptic_peptide_sequence_coverage_pct": getattr(study, "hdx_peptic_peptide_sequence_coverage_pct"),
        "deuterium_incorporation_mass_accuracy_ppm": getattr(study, "deuterium_incorporation_mass_accuracy_ppm"),
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
    repo = HdxMsConformationalModelerRepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "target_specimen": s.target_specimen,
            "analytical_modality": s.analytical_modality,
            "hdx_peptic_peptide_sequence_coverage_pct": getattr(s, "hdx_peptic_peptide_sequence_coverage_pct"),
            "deuterium_incorporation_mass_accuracy_ppm": getattr(s, "deuterium_incorporation_mass_accuracy_ppm"),
            "status": s.status,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in studies
    ]
