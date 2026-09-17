from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.gene_circuit_burden_repo import GeneCircuitBurdenRepository
from research.circuits.burden_engine import GeneCircuitBurdenEngine

router = APIRouter(prefix="/api/v1/circuit-burden", tags=["Gene Circuit Stability & Burden"])

class CircuitBurdenSimulateRequest(BaseModel):
    circuit_name: str = Field(..., example="Genetic Toggle Switch V3")
    host_organism: str = Field("E. coli K-12", example="E. coli K-12")
    promoter_strength_rpum: float = Field(1250.0, example=1250.0)
    cds_length_amino_acids: int = Field(450, example=450)
    copy_number_per_cell: int = Field(15, example=15)

@router.post("/simulate", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def simulate_gene_circuit_burden(
    request: CircuitBurdenSimulateRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Autonomous Synthetic Gene Circuit Stability & Metabolic Burden Forecaster.
    """
    engine = GeneCircuitBurdenEngine()
    repo = GeneCircuitBurdenRepository(db)

    # 1. Simulate metabolic burden
    res = engine.simulate_circuit_metabolic_burden(
        circuit_name=request.circuit_name,
        promoter_strength_rpum=request.promoter_strength_rpum,
        cds_length_amino_acids=request.cds_length_amino_acids,
        copy_number_per_cell=request.copy_number_per_cell,
        host_organism=request.host_organism,
    )

    # 2. Persist simulation
    sim = await repo.create_simulation(
        circuit_name=request.circuit_name,
        host_organism=request.host_organism,
        promoter_strength_rpum=request.promoter_strength_rpum,
        ribosome_allocation_pct=res["ribosome_allocation_pct"],
        growth_rate_penalty_pct=res["growth_rate_penalty_pct"],
        evolutionary_half_life_generations=res["evolutionary_half_life_generations"],
        circuit_failure_mode=res["circuit_failure_mode"],
    )

    # 3. Persist host capacity model
    await repo.add_host_capacity_model(
        simulation_id=sim.id,
        free_ribosome_pool_fraction=res["free_ribosome_pool_fraction"],
        atp_drain_flux_mmol_gdw_h=res["atp_drain_flux_mmol_gdw_h"],
        chaperone_load_index=res["chaperone_load_index"],
        metabolic_burden_status=res["metabolic_burden_status"],
    )

    hydrated = await repo.get_simulation_by_id(sim.id)

    return {
        "status": "SUCCESS",
        "simulation_id": hydrated.id,
        "circuit_name": hydrated.circuit_name,
        "host_organism": hydrated.host_organism,
        "ribosome_allocation_pct": hydrated.ribosome_allocation_pct,
        "growth_rate_penalty_pct": hydrated.growth_rate_penalty_pct,
        "evolutionary_half_life_generations": hydrated.evolutionary_half_life_generations,
        "circuit_failure_mode": hydrated.circuit_failure_mode,
        "free_ribosome_pool_fraction": res["free_ribosome_pool_fraction"],
        "atp_drain_flux_mmol_gdw_h": res["atp_drain_flux_mmol_gdw_h"],
        "metabolic_burden_status": res["metabolic_burden_status"],
    }

@router.get("/simulations", response_model=List[Dict[str, Any]])
async def list_circuit_simulations(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    repo = GeneCircuitBurdenRepository(db)
    sims = await repo.list_simulations(limit=limit)
    return [
        {
            "id": s.id,
            "circuit_name": s.circuit_name,
            "host_organism": s.host_organism,
            "ribosome_allocation_pct": s.ribosome_allocation_pct,
            "growth_rate_penalty_pct": s.growth_rate_penalty_pct,
            "evolutionary_half_life_generations": s.evolutionary_half_life_generations,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in sims
    ]

@router.get("/simulations/{sim_id}", response_model=Dict[str, Any])
async def get_circuit_simulation(
    sim_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    repo = GeneCircuitBurdenRepository(db)
    s = await repo.get_simulation_by_id(sim_id)
    if not s:
        raise HTTPException(status_code=404, detail="Circuit simulation not found")
    return {
        "id": s.id,
        "circuit_name": s.circuit_name,
        "host_organism": s.host_organism,
        "promoter_strength_rpum": s.promoter_strength_rpum,
        "ribosome_allocation_pct": s.ribosome_allocation_pct,
        "growth_rate_penalty_pct": s.growth_rate_penalty_pct,
        "evolutionary_half_life_generations": s.evolutionary_half_life_generations,
        "circuit_failure_mode": s.circuit_failure_mode,
        "capacity_models": [
            {
                "id": c.id,
                "free_ribosome_pool_fraction": c.free_ribosome_pool_fraction,
                "atp_drain_flux_mmol_gdw_h": c.atp_drain_flux_mmol_gdw_h,
                "chaperone_load_index": c.chaperone_load_index,
                "metabolic_burden_status": c.metabolic_burden_status,
            }
            for c in s.capacity_models
        ],
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }
