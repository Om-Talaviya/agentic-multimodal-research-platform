"""FastAPI routes for Phase 407: Deep Generative Therapeutic Antibody Humanization & T-Cell Epitope Ranker Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.antibody_humanness_immunogenicity_repo import AntibodyHumannessImmunogenicityRepository
from research.orchestration.antibody_humanness_immunogenicity_engine import AntibodyHumannessImmunogenicityEngine

router = APIRouter(prefix="/antibody-humanness-immunogenicity", tags=["antibody-humanness-immunogenicity"])


class AnalyzeAntibodyHumannessImmunogenicityRequest(BaseModel):
    name: str = Field(..., example="Autonomous Deep Generative Therapeutic Antibody Humanization & T-Cell Epitope Ranker Run")
    target_specimen: str = Field(default="Human Patient Cohort Sample")
    analytical_modality: str = Field(default="antibody-humanness-immunogenicity")
    input_scale: float = Field(default=1.0, ge=0.1, le=100.0)


class ItemProfileResponse(BaseModel):
    item_name: str
    profile_category: str
    quantitative_value: float
    log2_fold_change: float
    significance_score: float


class MetricTraceResponse(BaseModel):
    metric_dimension: str
    observed_value: float
    z_score: float
    p_value: float


class AntibodyHumannessImmunogenicityStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    antibody_humanness_t20_score_percentile: float
    mhc_class_ii_immunogenic_epitope_risk_reduction_pct: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=AntibodyHumannessImmunogenicityStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_antibody_humanness_immunogenicity(
    req: AnalyzeAntibodyHumannessImmunogenicityRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Deep Generative Therapeutic Antibody Humanization & T-Cell Epitope Ranker analysis and persist study record."""
    engine = AntibodyHumannessImmunogenicityEngine()
    analysis = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = AntibodyHumannessImmunogenicityRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=analysis.target_specimen,
        analytical_modality=analysis.analytical_modality,
        antibody_humanness_t20_score_percentile=getattr(analysis, "antibody_humanness_t20_score_percentile"),
        mhc_class_ii_immunogenic_epitope_risk_reduction_pct=getattr(analysis, "mhc_class_ii_immunogenic_epitope_risk_reduction_pct"),
        confidence_score=analysis.confidence_score,
        status="completed",
        summary_report=analysis.summary_report,
    )

    for it in analysis.item_profiles:
        await repo.add_item_profile(
            study_id=study.id,
            item_name=it.item_name,
            profile_category=it.profile_category,
            quantitative_value=it.quantitative_value,
            log2_fold_change=it.log2_fold_change,
            significance_score=it.significance_score,
        )

    for tr in analysis.metric_traces:
        await repo.add_metric_trace(
            study_id=study.id,
            metric_dimension=tr.metric_dimension,
            observed_value=tr.observed_value,
            z_score=tr.z_score,
            p_value=tr.p_value,
        )

    return AntibodyHumannessImmunogenicityStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        antibody_humanness_t20_score_percentile=getattr(study, "antibody_humanness_t20_score_percentile"),
        mhc_class_ii_immunogenic_epitope_risk_reduction_pct=getattr(study, "mhc_class_ii_immunogenic_epitope_risk_reduction_pct"),
        confidence_score=study.confidence_score,
        status=study.status,
        summary_report=study.summary_report,
        item_profiles=[
            ItemProfileResponse(
                item_name=it.item_name,
                profile_category=it.profile_category,
                quantitative_value=it.quantitative_value,
                log2_fold_change=it.log2_fold_change,
                significance_score=it.significance_score,
            ) for it in analysis.item_profiles
        ],
        metric_traces=[
            MetricTraceResponse(
                metric_dimension=tr.metric_dimension,
                observed_value=tr.observed_value,
                z_score=tr.z_score,
                p_value=tr.p_value,
            ) for tr in analysis.metric_traces
        ],
    )


@router.get("/studies", response_model=List[AntibodyHumannessImmunogenicityStudyResponse])
async def list_antibody_humanness_immunogenicity_studies(
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List historical Deep Generative Therapeutic Antibody Humanization & T-Cell Epitope Ranker studies."""
    repo = AntibodyHumannessImmunogenicityRepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        AntibodyHumannessImmunogenicityStudyResponse(
            id=s.id,
            name=s.name,
            target_specimen=s.target_specimen,
            analytical_modality=s.analytical_modality,
            antibody_humanness_t20_score_percentile=getattr(s, "antibody_humanness_t20_score_percentile"),
            mhc_class_ii_immunogenic_epitope_risk_reduction_pct=getattr(s, "mhc_class_ii_immunogenic_epitope_risk_reduction_pct"),
            confidence_score=s.confidence_score,
            status=s.status,
            summary_report=s.summary_report,
            item_profiles=[],
            metric_traces=[],
        ) for s in studies
    ]


@router.get("/studies/{study_id}", response_model=AntibodyHumannessImmunogenicityStudyResponse)
async def get_antibody_humanness_immunogenicity_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Retrieve details for a single Deep Generative Therapeutic Antibody Humanization & T-Cell Epitope Ranker study."""
    repo = AntibodyHumannessImmunogenicityRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")
    return AntibodyHumannessImmunogenicityStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        antibody_humanness_t20_score_percentile=getattr(study, "antibody_humanness_t20_score_percentile"),
        mhc_class_ii_immunogenic_epitope_risk_reduction_pct=getattr(study, "mhc_class_ii_immunogenic_epitope_risk_reduction_pct"),
        confidence_score=study.confidence_score,
        status=study.status,
        summary_report=study.summary_report,
        item_profiles=[],
        metric_traces=[],
    )
