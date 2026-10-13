"""FastAPI routes for Phase 446: Autonomous Spatial Epigenomic Histone H3K27me3 Polycomb Repressive Domain Spreading Modeler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.polycomb_epigenomic_domain_spreading_repo import PolycombEpigenomicDomainRepository
from research.orchestration.polycomb_epigenomic_domain_spreading_engine import PolycombEpigenomicDomainEngine

router = APIRouter(prefix="/polycomb-epigenomic-domain", tags=["polycomb-epigenomic-domain"])


class AnalyzePolycombEpigenomicDomainRequest(BaseModel):
    name: str = Field(..., example="Autonomous Spatial Epigenomic Histone H3K27me3 Polycomb Repressive Domain Spreading Modeler Run")
    target_specimen: str = Field(default="Pluripotent Embryonic Stem Cells Differentiation Locus Chromatin Super-Domain")
    analytical_modality: str = Field(default="polycomb-epigenomic-spreading")
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


class PolycombEpigenomicDomainStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    polycomb_spreading_velocity_bp_per_hr: float
    prc2_nucleosome_occupancy_ratio: float
    chromatin_compaction_density_nm: float
    transcriptional_repression_half_life_days: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=PolycombEpigenomicDomainStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_polycomb_epigenomic_domain_spreading(
    req: AnalyzePolycombEpigenomicDomainRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Spatial Epigenomic Histone H3K27me3 Polycomb Repressive Domain Spreading Modeler analysis and persist study."""
    engine = PolycombEpigenomicDomainEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = PolycombEpigenomicDomainRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        polycomb_spreading_velocity_bp_per_hr=result.polycomb_spreading_velocity_bp_per_hr,
        prc2_nucleosome_occupancy_ratio=result.prc2_nucleosome_occupancy_ratio,
        chromatin_compaction_density_nm=result.chromatin_compaction_density_nm,
        transcriptional_repression_half_life_days=result.transcriptional_repression_half_life_days,
        confidence_score=result.confidence_score,
        status="completed",
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

    return PolycombEpigenomicDomainStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        polycomb_spreading_velocity_bp_per_hr=study.polycomb_spreading_velocity_bp_per_hr,
        prc2_nucleosome_occupancy_ratio=study.prc2_nucleosome_occupancy_ratio,
        chromatin_compaction_density_nm=study.chromatin_compaction_density_nm,
        transcriptional_repression_half_life_days=study.transcriptional_repression_half_life_days,
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
            ) for it in result.item_profiles
        ],
        metric_traces=[
            MetricTraceResponse(
                metric_dimension=tr.metric_dimension,
                observed_value=tr.observed_value,
                z_score=tr.z_score,
                p_value=tr.p_value,
            ) for tr in result.metric_traces
        ],
    )


@router.get("/studies", response_model=List[PolycombEpigenomicDomainStudyResponse])
async def list_polycomb_epigenomic_domain_spreading_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Spatial Epigenomic Histone H3K27me3 Polycomb Repressive Domain Spreading Modeler studies."""
    repo = PolycombEpigenomicDomainRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=PolycombEpigenomicDomainStudyResponse)
async def get_polycomb_epigenomic_domain_spreading_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Spatial Epigenomic Histone H3K27me3 Polycomb Repressive Domain Spreading Modeler study by ID."""
    repo = PolycombEpigenomicDomainRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
