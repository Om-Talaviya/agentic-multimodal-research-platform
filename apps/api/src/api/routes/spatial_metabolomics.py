"""
FastAPI router for Spatial Metabolomics & MALDI Imaging MS (Phase 57).
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session
from database.repositories.spatial_metabolomics_repo import SpatialMetabolomicsRepository
from research.metabolomics.spatial_metabolomics_engine import SpatialMetabolomicsEngine

router = APIRouter(prefix="/spatial-metabolomics", tags=["Spatial Metabolomics"])


class CreateExperimentRequest(BaseModel):
    tissue_sample_id: str = Field(default="SAM-MALDI-2026-07")
    organ_type: str = Field(default="Glioblastoma Multiforme Tissue Section")
    matrix_compound: str = Field(default="DHB")
    spatial_resolution_um: float = Field(default=20.0)


@router.post("/experiments", status_code=status.HTTP_201_CREATED)
async def create_spatial_metabolomics_experiment(
    request: CreateExperimentRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Executes spatial metabolite ion profiling and FBA flux rate matrix computation."""
    repo = SpatialMetabolomicsRepository(db)
    exp = await repo.create_experiment(
        tissue_sample_id=request.tissue_sample_id,
        organ_type=request.organ_type,
        matrix_compound=request.matrix_compound,
        spatial_resolution_um=request.spatial_resolution_um,
    )

    sim_result = SpatialMetabolomicsEngine.simulate_spatial_metabolome(
        sample_id=request.tissue_sample_id,
        organ_type=request.organ_type,
    )

    await repo.add_metabolites_and_flux(
        experiment_id=exp.id,
        metabolites_data=sim_result["metabolites"],
        flux_data=sim_result["flux_routes"],
    )

    return await repo.get_experiment(exp.id)


@router.get("/experiments")
async def list_experiments(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
):
    """Lists spatial metabolomics runs."""
    repo = SpatialMetabolomicsRepository(db)
    return await repo.list_experiments(limit=limit)


@router.get("/experiments/{experiment_id}")
async def get_experiment(
    experiment_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieves full experiment details with spatial profiles and flux balances."""
    repo = SpatialMetabolomicsRepository(db)
    exp = await repo.get_experiment(experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Spatial metabolomics experiment not found")
    return exp
