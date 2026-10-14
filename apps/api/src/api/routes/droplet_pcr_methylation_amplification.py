"""FastAPI routes for Phase 486: Autonomous Microfluidic Droplet PCR Digital Methylation Specific Amplification Modeler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.droplet_pcr_methylation_amplification_repo import DropletPcrMethylationAmplificationRepository
from research.orchestration.droplet_pcr_methylation_amplification_engine import DropletPcrMethylationAmplificationEngine

router = APIRouter(prefix="/droplet-pcr-methylation-amplification", tags=["droplet-pcr-methylation-amplification"])


class AnalyzeDropletPcrMethylationAmplificationRequest(BaseModel):
    name: str = Field(..., example="Autonomous Microfluidic Droplet PCR Digital Methylation Specific Amplification Modeler Run")
    target_specimen: str = Field(default="Bisulfite-Converted ctDNA in 20,000 Microfluidic Fluorinated Oil Picoliter Droplets")
    analytical_modality: str = Field(default="droplet-pcr-methylation-amplification")
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


class DropletPcrMethylationAmplificationStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    fractional_methylation_abundance_pct: float
    poisson_droplet_partition_occupancy_lambda: float
    false_positive_droplet_count_per_million: float
    target_dna_amplification_efficiency: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=DropletPcrMethylationAmplificationStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_droplet_pcr_methylation_amplification(
    req: AnalyzeDropletPcrMethylationAmplificationRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Microfluidic Droplet PCR Digital Methylation Specific Amplification Modeler analysis and persist study."""
    engine = DropletPcrMethylationAmplificationEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = DropletPcrMethylationAmplificationRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        fractional_methylation_abundance_pct=result.fractional_methylation_abundance_pct,
        poisson_droplet_partition_occupancy_lambda=result.poisson_droplet_partition_occupancy_lambda,
        false_positive_droplet_count_per_million=result.false_positive_droplet_count_per_million,
        target_dna_amplification_efficiency=result.target_dna_amplification_efficiency,
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

    return DropletPcrMethylationAmplificationStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        fractional_methylation_abundance_pct=study.fractional_methylation_abundance_pct,
        poisson_droplet_partition_occupancy_lambda=study.poisson_droplet_partition_occupancy_lambda,
        false_positive_droplet_count_per_million=study.false_positive_droplet_count_per_million,
        target_dna_amplification_efficiency=study.target_dna_amplification_efficiency,
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


@router.get("/studies", response_model=List[DropletPcrMethylationAmplificationStudyResponse])
async def list_droplet_pcr_methylation_amplification_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Microfluidic Droplet PCR Digital Methylation Specific Amplification Modeler studies."""
    repo = DropletPcrMethylationAmplificationRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=DropletPcrMethylationAmplificationStudyResponse)
async def get_droplet_pcr_methylation_amplification_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Microfluidic Droplet PCR Digital Methylation Specific Amplification Modeler study by ID."""
    repo = DropletPcrMethylationAmplificationRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
