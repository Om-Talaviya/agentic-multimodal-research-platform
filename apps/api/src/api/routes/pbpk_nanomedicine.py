"""
FastAPI router for Nanomedicine PBPK Simulator (Phase 60).
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session
from database.repositories.pbpk_nanomedicine_repo import NanomedicinePBPKRepository
from research.pbpk.pbpk_engine import NanomedicinePBPKEngine

router = APIRouter(prefix="/pbpk-nanomedicine", tags=["Nanomedicine PBPK Simulator"])


class CreateSimulationRequest(BaseModel):
    formulation_name: str = Field(default="LNP-mRNA-Oncology-01")
    carrier_type: str = Field(default="Lipid Nanoparticle (LNP)")
    hydrodynamic_diameter_nm: float = Field(default=85.0)
    zeta_potential_mv: float = Field(default=-3.5)
    pegylation_density_pct: float = Field(default=1.5)
    dose_mg_kg: float = Field(default=1.0)
    tumor_epr_permeability_index: float = Field(default=0.85)


@router.post("/simulations", status_code=status.HTTP_201_CREATED)
async def run_pbpk_simulation(
    request: CreateSimulationRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Executes 7-compartment PBPK nanomedicine biodistribution simulation."""
    repo = NanomedicinePBPKRepository(db)
    sim = await repo.create_simulation(
        formulation_name=request.formulation_name,
        carrier_type=request.carrier_type,
        hydrodynamic_diameter_nm=request.hydrodynamic_diameter_nm,
        zeta_potential_mv=request.zeta_potential_mv,
        pegylation_density_pct=request.pegylation_density_pct,
        dose_mg_kg=request.dose_mg_kg,
        tumor_epr_permeability_index=request.tumor_epr_permeability_index,
    )

    pbpk_result = NanomedicinePBPKEngine.simulate_pbpk(
        formulation_name=request.formulation_name,
        diameter_nm=request.hydrodynamic_diameter_nm,
        zeta_mv=request.zeta_potential_mv,
        peg_pct=request.pegylation_density_pct,
        dose_mg_kg=request.dose_mg_kg,
        epr_index=request.tumor_epr_permeability_index,
    )

    return await repo.add_compartments_and_clearance(
        simulation_id=sim.id,
        compartments_data=pbpk_result["compartments"],
        clearance_data=pbpk_result["clearance_pathways"],
    )


@router.get("/simulations")
async def list_simulations(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
):
    """Lists PBPK nanomedicine simulations."""
    repo = NanomedicinePBPKRepository(db)
    return await repo.list_simulations(limit=limit)


@router.get("/simulations/{simulation_id}")
async def get_simulation(
    simulation_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieves full simulation results across all compartments and clearance pathways."""
    repo = NanomedicinePBPKRepository(db)
    sim = await repo.get_simulation(simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail="PBPK simulation not found")
    return sim
