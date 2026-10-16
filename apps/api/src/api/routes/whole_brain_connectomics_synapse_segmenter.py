"""FastAPI routes for Phase 563: Autonomous Whole-Brain Nanoscale Connectomics Automated Volume Electron Microscopy Synapse Segmenter."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.whole_brain_connectomics_synapse_segmenter_repo import WholeBrainConnectomicsSynapseSegmenterRepository
from research.orchestration.whole_brain_connectomics_synapse_segmenter_engine import WholeBrainConnectomicsSynapseSegmenterEngine

router = APIRouter(prefix="/whole-brain-connectomics-synapse-segmenter", tags=["whole-brain-connectomics-synapse-segmenter"])


class AnalyzeWholeBrainConnectomicsSynapseSegmenterRequest(BaseModel):
    name: str = Field(..., example="Autonomous Whole-Brain Nanoscale Connectomics Automated Volume Electron Microscopy Synapse Segmenter Run")
    target_specimen: str = Field(default="Serial Section Electron Tomography (FIB-SEM) of Adult Drosophila Melanogaster Central Brain at 4x4x4 nm3 Voxel Resolution")
    analytical_modality: str = Field(default="whole-brain-connectomics-segmentation")
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


class WholeBrainConnectomicsSynapseSegmenterStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    synaptic_junction_detection_f1_score: float
    t_bar_active_zone_reconstruction_precision: float
    neurite_skeletonization_topological_accuracy: float
    segmented_synaptic_density_per_100_um3: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=WholeBrainConnectomicsSynapseSegmenterStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_whole_brain_connectomics_synapse_segmenter(
    req: AnalyzeWholeBrainConnectomicsSynapseSegmenterRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Whole-Brain Nanoscale Connectomics Automated Volume Electron Microscopy Synapse Segmenter analysis and persist study."""
    engine = WholeBrainConnectomicsSynapseSegmenterEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = WholeBrainConnectomicsSynapseSegmenterRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        synaptic_junction_detection_f1_score=result.synaptic_junction_detection_f1_score,
        t_bar_active_zone_reconstruction_precision=result.t_bar_active_zone_reconstruction_precision,
        neurite_skeletonization_topological_accuracy=result.neurite_skeletonization_topological_accuracy,
        segmented_synaptic_density_per_100_um3=result.segmented_synaptic_density_per_100_um3,
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

    return WholeBrainConnectomicsSynapseSegmenterStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        synaptic_junction_detection_f1_score=study.synaptic_junction_detection_f1_score,
        t_bar_active_zone_reconstruction_precision=study.t_bar_active_zone_reconstruction_precision,
        neurite_skeletonization_topological_accuracy=study.neurite_skeletonization_topological_accuracy,
        segmented_synaptic_density_per_100_um3=study.segmented_synaptic_density_per_100_um3,
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


@router.get("/studies", response_model=List[WholeBrainConnectomicsSynapseSegmenterStudyResponse])
async def list_whole_brain_connectomics_synapse_segmenter_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Whole-Brain Nanoscale Connectomics Automated Volume Electron Microscopy Synapse Segmenter studies."""
    repo = WholeBrainConnectomicsSynapseSegmenterRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=WholeBrainConnectomicsSynapseSegmenterStudyResponse)
async def get_whole_brain_connectomics_synapse_segmenter_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Whole-Brain Nanoscale Connectomics Automated Volume Electron Microscopy Synapse Segmenter study by ID."""
    repo = WholeBrainConnectomicsSynapseSegmenterRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
