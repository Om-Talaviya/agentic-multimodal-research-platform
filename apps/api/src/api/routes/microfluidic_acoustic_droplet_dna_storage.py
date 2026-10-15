"""FastAPI routes for Phase 545: Autonomous Microfluidic High-Density Acoustic Droplet Synthetic DNA Digital Archival Writer & Reader."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.microfluidic_acoustic_droplet_dna_storage_repo import MicrofluidicAcousticDropletDnaStorageRepository
from research.orchestration.microfluidic_acoustic_droplet_dna_storage_engine import MicrofluidicAcousticDropletDnaStorageEngine

router = APIRouter(prefix="/microfluidic-acoustic-droplet-dna-storage", tags=["microfluidic-acoustic-droplet-dna-storage"])


class AnalyzeMicrofluidicAcousticDropletDnaStorageRequest(BaseModel):
    name: str = Field(..., example="Autonomous Microfluidic High-Density Acoustic Droplet Synthetic DNA Digital Archival Writer & Reader Run")
    target_specimen: str = Field(default="Acoustic Ejection Picoliter Well Plate containing Encoded 100-Mbyte Synthetic Oligo Pool with RS ECC")
    analytical_modality: str = Field(default="acoustic-droplet-dna-archival")
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


class MicrofluidicAcousticDropletDnaStorageStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    dna_archival_data_density_petabytes_per_gram: float
    acoustic_droplet_dispensing_throughput_khz: float
    reed_solomon_error_correction_recovery_pct: float
    per_base_synthesis_accuracy_pct: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=MicrofluidicAcousticDropletDnaStorageStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_microfluidic_acoustic_droplet_dna_storage(
    req: AnalyzeMicrofluidicAcousticDropletDnaStorageRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Microfluidic High-Density Acoustic Droplet Synthetic DNA Digital Archival Writer & Reader analysis and persist study."""
    engine = MicrofluidicAcousticDropletDnaStorageEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = MicrofluidicAcousticDropletDnaStorageRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        dna_archival_data_density_petabytes_per_gram=result.dna_archival_data_density_petabytes_per_gram,
        acoustic_droplet_dispensing_throughput_khz=result.acoustic_droplet_dispensing_throughput_khz,
        reed_solomon_error_correction_recovery_pct=result.reed_solomon_error_correction_recovery_pct,
        per_base_synthesis_accuracy_pct=result.per_base_synthesis_accuracy_pct,
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

    return MicrofluidicAcousticDropletDnaStorageStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        dna_archival_data_density_petabytes_per_gram=study.dna_archival_data_density_petabytes_per_gram,
        acoustic_droplet_dispensing_throughput_khz=study.acoustic_droplet_dispensing_throughput_khz,
        reed_solomon_error_correction_recovery_pct=study.reed_solomon_error_correction_recovery_pct,
        per_base_synthesis_accuracy_pct=study.per_base_synthesis_accuracy_pct,
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


@router.get("/studies", response_model=List[MicrofluidicAcousticDropletDnaStorageStudyResponse])
async def list_microfluidic_acoustic_droplet_dna_storage_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Microfluidic High-Density Acoustic Droplet Synthetic DNA Digital Archival Writer & Reader studies."""
    repo = MicrofluidicAcousticDropletDnaStorageRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=MicrofluidicAcousticDropletDnaStorageStudyResponse)
async def get_microfluidic_acoustic_droplet_dna_storage_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Microfluidic High-Density Acoustic Droplet Synthetic DNA Digital Archival Writer & Reader study by ID."""
    repo = MicrofluidicAcousticDropletDnaStorageRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
