"""API Routes for PK/PD Simulation & PBPK Modeler (Phase 99)."""

import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.pkpd_model_repo import PkPdSimulationRepository
from research.clinical.pkpd_engine import PkPdModelerEngine

router = APIRouter(prefix="/pkpd-simulation", tags=["PK/PD & PBPK Modeler"])


class PkPdSimulationRequest(BaseModel):
    drug_name: str = Field(..., example="Osimertinib")
    dose_mg: float = Field(..., example=80.0)
    route: str = Field(default="ORAL", example="ORAL")
    dosing_interval_hours: float = Field(default=24.0, example=24.0)
    bioavailability: float = Field(default=0.85, example=0.85)
    clearance_l_hr: float = Field(default=4.2, example=4.2)
    vd_central_l: float = Field(default=28.0, example=28.0)
    workspace_id: Optional[str] = None


@router.post("/simulate", status_code=status.HTTP_201_CREATED)
async def simulate_pkpd_regimen(
    request: PkPdSimulationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Simulate 2-compartment clearance PK profiles, organ Kp values, and Hill PD target occupancy."""
    engine = PkPdModelerEngine()
    result = engine.simulate_regimen(
        drug_name=request.drug_name,
        dose_mg=request.dose_mg,
        route=request.route,
        dosing_interval_hours=request.dosing_interval_hours,
        bioavailability=request.bioavailability,
        clearance_l_hr=request.clearance_l_hr,
        vd_central_l=request.vd_central_l,
    )

    repo = PkPdSimulationRepository(db)
    ws_id = uuid.UUID(request.workspace_id) if request.workspace_id else uuid.uuid4()

    sim = await repo.create_simulation(
        workspace_id=ws_id,
        drug_name=result["drug_name"],
        route_of_administration=result["route_of_administration"],
        dose_mg=result["dose_mg"],
        dosing_interval_hours=result["dosing_interval_hours"],
        cmax_ug_ml=result["cmax_ug_ml"],
        tmax_hours=result["tmax_hours"],
        auc_inf_ug_hr_ml=result["auc_inf_ug_hr_ml"],
        elimination_half_life_hours=result["elimination_half_life_hours"],
        clearance_l_per_hr=result["clearance_l_per_hr"],
        volume_distribution_l=result["volume_distribution_l"],
        therapeutic_window_compliance=result["therapeutic_window_compliance"],
        simulation_metadata={"summary": result["summary"]},
    )

    for tc in result["tissue_concentrations"]:
        await repo.add_tissue_concentration(
            simulation_id=sim.id,
            tissue_organ=tc["tissue_organ"],
            kp_partition_coefficient=tc["kp_partition_coefficient"],
            cmax_tissue_ug_g=tc["cmax_tissue_ug_g"],
            auc_tissue_ug_hr_g=tc["auc_tissue_ug_hr_g"],
        )

    for pe in result["pd_effects"]:
        await repo.add_pd_effect(
            simulation_id=sim.id,
            biomarker_name=pe["biomarker_name"],
            emax_percent=pe["emax_percent"],
            ec50_ug_ml=pe["ec50_ug_ml"],
            hill_coefficient=pe["hill_coefficient"],
            max_effect_observed=pe["max_effect_observed"],
            duration_above_ic90_hours=pe["duration_above_ic90_hours"],
        )

    return {
        "status": "SUCCESS",
        "simulation_id": str(sim.id),
        "drug_name": sim.drug_name,
        "cmax_ug_ml": sim.cmax_ug_ml,
        "auc_inf_ug_hr_ml": sim.auc_inf_ug_hr_ml,
        "elimination_half_life_hours": sim.elimination_half_life_hours,
        "therapeutic_window_compliance": sim.therapeutic_window_compliance,
        "tissue_concentrations": result["tissue_concentrations"],
        "pd_effects": result["pd_effects"],
        "summary": result["summary"],
    }


@router.get("/simulations/{simulation_id}")
async def get_simulation_details(
    simulation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Retrieve full PK/PD simulation and organ partition profile."""
    repo = PkPdSimulationRepository(db)
    try:
        sid = uuid.UUID(simulation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid simulation UUID format")

    sim = await repo.get_simulation(sid)
    if not sim:
        raise HTTPException(status_code=404, detail="PK/PD simulation not found")

    return {
        "id": str(sim.id),
        "drug_name": sim.drug_name,
        "dose_mg": sim.dose_mg,
        "route_of_administration": sim.route_of_administration,
        "cmax_ug_ml": sim.cmax_ug_ml,
        "auc_inf_ug_hr_ml": sim.auc_inf_ug_hr_ml,
        "elimination_half_life_hours": sim.elimination_half_life_hours,
        "therapeutic_window_compliance": sim.therapeutic_window_compliance,
        "tissue_concentrations": [
            {
                "tissue_organ": tc.tissue_organ,
                "kp_partition_coefficient": tc.kp_partition_coefficient,
                "cmax_tissue_ug_g": tc.cmax_tissue_ug_g,
                "auc_tissue_ug_hr_g": tc.auc_tissue_ug_hr_g,
            }
            for tc in sim.tissue_concentrations
        ],
        "pd_effects": [
            {
                "biomarker_name": pe.biomarker_name,
                "max_effect_observed": pe.max_effect_observed,
                "duration_above_ic90_hours": pe.duration_above_ic90_hours,
            }
            for pe in sim.pd_effects
        ],
    }
