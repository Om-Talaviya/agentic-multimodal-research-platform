"""FastAPI routes for Phase 420: Autonomous Single-Cell Multi-Modal CITE-seq & TCR Clonotype Immune Synapse Dynamics Deconvolver."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.citeseq_tcr_immune_synapse_repo import CiteseqTcrImmuneSynapseRepository
from research.orchestration.citeseq_tcr_immune_synapse_engine import CiteseqTcrImmuneSynapseEngine

router = APIRouter(prefix="/citeseq-tcr-immune-synapse", tags=["citeseq-tcr-immune-synapse"])


class AnalyzeCiteseqTcrImmuneSynapseRequest(BaseModel):
    name: str = Field(..., example="Autonomous Single-Cell Multi-Modal CITE-seq & TCR Clonotype Immune Synapse Dynamics Deconvolver Run")
    target_specimen: str = Field(default="Human CD8+ Tumor-Infiltrating Lymphocytes with pMHC Multimer")
    analytical_modality: str = Field(default="citeseq-tcr-synapse")
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


class CiteseqTcrImmuneSynapseStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    immune_synapse_contact_area_um2: float
    surface_protein_abundance_umi: float
    tcr_clonotype_affinity_score: float
    cytotoxic_granule_polarization_ratio: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=CiteseqTcrImmuneSynapseStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_citeseq_tcr_immune_synapse(
    req: AnalyzeCiteseqTcrImmuneSynapseRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Single-Cell Multi-Modal CITE-seq & TCR Clonotype Immune Synapse Dynamics Deconvolver analysis and persist study."""
    engine = CiteseqTcrImmuneSynapseEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = CiteseqTcrImmuneSynapseRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        immune_synapse_contact_area_um2=result.immune_synapse_contact_area_um2,
        surface_protein_abundance_umi=result.surface_protein_abundance_umi,
        tcr_clonotype_affinity_score=result.tcr_clonotype_affinity_score,
        cytotoxic_granule_polarization_ratio=result.cytotoxic_granule_polarization_ratio,
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

    return CiteseqTcrImmuneSynapseStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        immune_synapse_contact_area_um2=study.immune_synapse_contact_area_um2,
        surface_protein_abundance_umi=study.surface_protein_abundance_umi,
        tcr_clonotype_affinity_score=study.tcr_clonotype_affinity_score,
        cytotoxic_granule_polarization_ratio=study.cytotoxic_granule_polarization_ratio,
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


@router.get("/studies", response_model=List[CiteseqTcrImmuneSynapseStudyResponse])
async def list_citeseq_tcr_immune_synapse_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Single-Cell Multi-Modal CITE-seq & TCR Clonotype Immune Synapse Dynamics Deconvolver studies."""
    repo = CiteseqTcrImmuneSynapseRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=CiteseqTcrImmuneSynapseStudyResponse)
async def get_citeseq_tcr_immune_synapse_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Single-Cell Multi-Modal CITE-seq & TCR Clonotype Immune Synapse Dynamics Deconvolver study by ID."""
    repo = CiteseqTcrImmuneSynapseRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
