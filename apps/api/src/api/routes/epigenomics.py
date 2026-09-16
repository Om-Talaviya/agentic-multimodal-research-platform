"""
FastAPI router for Epigenomics Chromatin Accessibility & ATAC-seq (Phase 56).
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session
from database.repositories.epigenomics_repo import EpigenomicsRepository
from research.epigenomics.epigenomics_engine import EpigenomicsEngine

router = APIRouter(prefix="/epigenomics", tags=["Epigenomics & Chromatin"])


class CreateExperimentRequest(BaseModel):
    sample_id: str = Field(default="SAM-ATAC-2026-01")
    tissue_type: str = Field(default="CD8+ T-cell Exhaustion")
    assay_type: str = Field(default="ATAC-seq")
    sequencing_depth_millions: float = Field(default=52.4)
    target_genes: List[str] = Field(default=["PDCD1", "HAVCR2", "LAG3", "TOX", "TCF7", "IFNG", "IL2"])


@router.post("/experiments", status_code=status.HTTP_201_CREATED)
async def create_epigenomic_experiment(
    request: CreateExperimentRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Executes ATAC-seq peak calling and TF motif enrichment identification."""
    repo = EpigenomicsRepository(db)
    exp = await repo.create_experiment(
        sample_id=request.sample_id,
        tissue_type=request.tissue_type,
        assay_type=request.assay_type,
        sequencing_depth_millions=request.sequencing_depth_millions,
    )

    peaks_data = EpigenomicsEngine.call_peaks_and_motifs(
        sample_id=request.sample_id,
        target_genes=request.target_genes,
        depth_m=request.sequencing_depth_millions,
    )

    await repo.add_peaks_with_motifs(exp.id, peaks_data)
    return await repo.get_experiment(exp.id)


@router.get("/experiments")
async def list_experiments(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
):
    """Lists epigenomics experiments."""
    repo = EpigenomicsRepository(db)
    return await repo.list_experiments(limit=limit)


@router.get("/experiments/{experiment_id}")
async def get_experiment(
    experiment_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieves full experiment details with chromatin peaks and motifs."""
    repo = EpigenomicsRepository(db)
    exp = await repo.get_experiment(experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Epigenomics experiment not found")
    return exp


@router.get("/experiments/{experiment_id}/peaks")
async def query_peaks(
    experiment_id: str,
    chromosome: Optional[str] = Query(None),
    annotation: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
):
    """Filters chromatin accessibility peaks by chromosome or functional annotation."""
    repo = EpigenomicsRepository(db)
    return await repo.query_peaks(
        experiment_id=experiment_id,
        chromosome=chromosome,
        annotation=annotation,
        limit=limit,
    )
