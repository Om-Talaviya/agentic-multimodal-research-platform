"""FastAPI routes for Phase 514: Autonomous Equivariant Graph Neural Network TCR-pMHC Interface Binding Energy Forecaster."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.deep_learning_tcr_pmhc_docking_energy_repo import DeepLearningTcrPmhcDockingEnergyRepository
from research.orchestration.deep_learning_tcr_pmhc_docking_energy_engine import DeepLearningTcrPmhcDockingEnergyEngine

router = APIRouter(prefix="/deep-learning-tcr-pmhc-docking-energy", tags=["deep-learning-tcr-pmhc-docking-energy"])


class AnalyzeDeepLearningTcrPmhcDockingEnergyRequest(BaseModel):
    name: str = Field(..., example="Autonomous Equivariant Graph Neural Network TCR-pMHC Interface Binding Energy Forecaster Run")
    target_specimen: str = Field(default="Structure-Resolved Complex of Human CD8+ TCR with Cancer-Testis Neoantigen NY-ESO-1 HLA-A*02:01")
    analytical_modality: str = Field(default="egnn-tcr-pmhc-docking")
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


class DeepLearningTcrPmhcDockingEnergyStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    predicted_binding_free_energy_delta_G_kcal_mol: float
    cdr3_loop_interface_contact_rmsd_angstrom: float
    allotype_cross_reactivity_prediction_auroc: float
    dissociation_constant_kd_nM: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=DeepLearningTcrPmhcDockingEnergyStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_deep_learning_tcr_pmhc_docking_energy(
    req: AnalyzeDeepLearningTcrPmhcDockingEnergyRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Equivariant Graph Neural Network TCR-pMHC Interface Binding Energy Forecaster analysis and persist study."""
    engine = DeepLearningTcrPmhcDockingEnergyEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = DeepLearningTcrPmhcDockingEnergyRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        predicted_binding_free_energy_delta_G_kcal_mol=result.predicted_binding_free_energy_delta_G_kcal_mol,
        cdr3_loop_interface_contact_rmsd_angstrom=result.cdr3_loop_interface_contact_rmsd_angstrom,
        allotype_cross_reactivity_prediction_auroc=result.allotype_cross_reactivity_prediction_auroc,
        dissociation_constant_kd_nM=result.dissociation_constant_kd_nM,
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

    return DeepLearningTcrPmhcDockingEnergyStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        predicted_binding_free_energy_delta_G_kcal_mol=study.predicted_binding_free_energy_delta_G_kcal_mol,
        cdr3_loop_interface_contact_rmsd_angstrom=study.cdr3_loop_interface_contact_rmsd_angstrom,
        allotype_cross_reactivity_prediction_auroc=study.allotype_cross_reactivity_prediction_auroc,
        dissociation_constant_kd_nM=study.dissociation_constant_kd_nM,
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


@router.get("/studies", response_model=List[DeepLearningTcrPmhcDockingEnergyStudyResponse])
async def list_deep_learning_tcr_pmhc_docking_energy_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Equivariant Graph Neural Network TCR-pMHC Interface Binding Energy Forecaster studies."""
    repo = DeepLearningTcrPmhcDockingEnergyRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=DeepLearningTcrPmhcDockingEnergyStudyResponse)
async def get_deep_learning_tcr_pmhc_docking_energy_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Equivariant Graph Neural Network TCR-pMHC Interface Binding Energy Forecaster study by ID."""
    repo = DeepLearningTcrPmhcDockingEnergyRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
