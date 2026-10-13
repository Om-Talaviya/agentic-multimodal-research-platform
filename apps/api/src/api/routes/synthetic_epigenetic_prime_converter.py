"""FastAPI routes for Phase 448: Autonomous Synthetic Epigenetic Prime-Converter Base Insertion & Inverted Repeat Profiler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.synthetic_epigenetic_prime_converter_repo import SyntheticEpigeneticPrimeConverterRepository
from research.orchestration.synthetic_epigenetic_prime_converter_engine import SyntheticEpigeneticPrimeConverterEngine

router = APIRouter(prefix="/synthetic-epigenetic-prime-converter", tags=["synthetic-epigenetic-prime-converter"])


class AnalyzeSyntheticEpigeneticPrimeConverterRequest(BaseModel):
    name: str = Field(..., example="Autonomous Synthetic Epigenetic Prime-Converter Base Insertion & Inverted Repeat Profiler Run")
    target_specimen: str = Field(default="Engineered PegRNA / Cas9-Nickase Prime Editor Complex on Methylated CpG Island")
    analytical_modality: str = Field(default="epigenetic-prime-conversion")
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


class SyntheticEpigeneticPrimeConverterStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    peg_rna_extension_annealing_tm_celsius: float
    prime_conversion_efficiency_percentage: float
    cpg_demethylation_retention_ratio: float
    insertion_fidelity_indel_free_score: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=SyntheticEpigeneticPrimeConverterStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_synthetic_epigenetic_prime_converter(
    req: AnalyzeSyntheticEpigeneticPrimeConverterRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Synthetic Epigenetic Prime-Converter Base Insertion & Inverted Repeat Profiler analysis and persist study."""
    engine = SyntheticEpigeneticPrimeConverterEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SyntheticEpigeneticPrimeConverterRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        peg_rna_extension_annealing_tm_celsius=result.peg_rna_extension_annealing_tm_celsius,
        prime_conversion_efficiency_percentage=result.prime_conversion_efficiency_percentage,
        cpg_demethylation_retention_ratio=result.cpg_demethylation_retention_ratio,
        insertion_fidelity_indel_free_score=result.insertion_fidelity_indel_free_score,
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

    return SyntheticEpigeneticPrimeConverterStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        peg_rna_extension_annealing_tm_celsius=study.peg_rna_extension_annealing_tm_celsius,
        prime_conversion_efficiency_percentage=study.prime_conversion_efficiency_percentage,
        cpg_demethylation_retention_ratio=study.cpg_demethylation_retention_ratio,
        insertion_fidelity_indel_free_score=study.insertion_fidelity_indel_free_score,
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


@router.get("/studies", response_model=List[SyntheticEpigeneticPrimeConverterStudyResponse])
async def list_synthetic_epigenetic_prime_converter_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Synthetic Epigenetic Prime-Converter Base Insertion & Inverted Repeat Profiler studies."""
    repo = SyntheticEpigeneticPrimeConverterRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SyntheticEpigeneticPrimeConverterStudyResponse)
async def get_synthetic_epigenetic_prime_converter_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Synthetic Epigenetic Prime-Converter Base Insertion & Inverted Repeat Profiler study by ID."""
    repo = SyntheticEpigeneticPrimeConverterRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
