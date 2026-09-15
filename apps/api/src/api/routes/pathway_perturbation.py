"""
FastAPI Route Handlers for Phase 48: Multi-Omics Pathway Perturbation & Causal Signaling.
"""
import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session, get_current_user
from database.models.user import User as DBUser
from database.repositories.pathway_perturbation_repo import PathwayPerturbationRepository
from research.pathway_perturbation_engine import PathwayPerturbationEngine

router = APIRouter(prefix="/pathways", tags=["Multi-Omics Pathway Perturbation (Phase 48)"])

class PerturbationSimRequest(BaseModel):
    title: str = Field(..., example="Dynamic ODE Simulation of KRAS-G12C Knockdown in A549 Cells")
    target_node: str = Field(..., example="KRAS_G12C")
    cell_line: str = Field(default="A549 (Lung Adenocarcinoma)", example="A549")
    perturbation_type: str = Field(default="CRISPR_KO", example="CRISPR_KO")
    time_course_hours: int = Field(default=48, example=48)

class ExperimentResponse(BaseModel):
    id: uuid.UUID
    title: str
    cell_line: str
    perturbation_type: str
    omics_layers: List[str]
    status: str
    created_at: Any

    class Config:
        from_attributes = True

@router.post("/simulate", response_model=ExperimentResponse, status_code=status.HTTP_201_CREATED)
async def simulate_and_create_experiment(
    payload: PerturbationSimRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: DBUser = Depends(get_current_user)
):
    engine = PathwayPerturbationEngine()
    result = engine.simulate_perturbation(
        title=payload.title,
        target_node=payload.target_node,
        cell_line=payload.cell_line,
        perturbation_type=payload.perturbation_type,
        time_course_hours=payload.time_course_hours
    )

    repo = PathwayPerturbationRepository(db)
    exp = await repo.create_experiment(
        title=result["title"],
        cell_line=result["cell_line"],
        perturbation_type=result["perturbation_type"],
        omics_layers=result["omics_layers"],
        user_id=current_user.id
    )

    casc = result["cascade"]
    await repo.add_cascade(
        experiment_id=exp.id,
        pathway_name=casc["pathway_name"],
        node_count=casc["node_count"],
        feedback_loops_count=casc["feedback_loops_count"],
        steady_state_activation=casc["steady_state_activation"],
        cascade_topology=casc["topology"]
    )

    sim = result["simulation"]
    await repo.add_simulation(
        experiment_id=exp.id,
        target_node=sim["target_node"],
        inhibition_efficiency=sim["inhibition_efficiency"],
        downstream_phospho_delta=sim["downstream_phospho_delta"],
        metabolic_flux_shift=sim["metabolic_flux_shift"],
        time_course_hours=sim["time_course_hours"],
        time_series_trajectories=sim["trajectories"],
        bypass_mechanisms=sim["bypass_mechanisms"]
    )

    return exp

@router.get("/experiments", response_model=List[ExperimentResponse])
async def list_experiments(
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session),
    current_user: DBUser = Depends(get_current_user)
):
    repo = PathwayPerturbationRepository(db)
    return await repo.list_experiments(limit=limit)

@router.get("/experiments/{exp_id}")
async def get_experiment_details(
    exp_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: DBUser = Depends(get_current_user)
):
    repo = PathwayPerturbationRepository(db)
    exp = await repo.get_experiment(exp_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Multi-Omics experiment not found")
    return {
        "id": str(exp.id),
        "title": exp.title,
        "cell_line": exp.cell_line,
        "perturbation_type": exp.perturbation_type,
        "omics_layers": exp.omics_layers,
        "cascades": [
            {
                "name": c.pathway_name,
                "node_count": c.node_count,
                "feedback_loops": c.feedback_loops_count,
                "steady_state": c.steady_state_activation,
                "topology": c.cascade_topology
            } for c in exp.cascades
        ],
        "simulations": [
            {
                "target_node": s.target_node,
                "inhibition_pct": s.inhibition_efficiency_pct,
                "phospho_delta": s.downstream_phospho_delta_pct,
                "flux_shift": s.metabolic_flux_shift_pct,
                "time_course": s.time_course_hours,
                "trajectories": s.time_series_trajectories,
                "bypass_mechanisms": s.bypass_resistance_mechanisms
            } for s in exp.simulations
        ]
    }
