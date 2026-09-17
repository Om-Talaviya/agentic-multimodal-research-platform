"""REST API endpoints for Single-Molecule FRET (smFRET) Kinetics."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.models import User
from database.repositories.smfret_repo import SmFRETRepository
from research.smfret.smfret_engine import SmFRETKineticsEngine

router = APIRouter(prefix="/api/v1/smfret", tags=["Single-Molecule FRET Kinetics"])
engine = SmFRETKineticsEngine()


class TraceInput(BaseModel):
    molecule_index: int
    total_frames: int = 500
    mean_fret_efficiency: float = 0.5
    photobleaching_frame: Optional[int] = None
    trace_data_json: List[Dict[str, Any]] = []


class SmFRETAnalysisRequest(BaseModel):
    experiment_title: str
    macromolecule_name: str
    donor_fluorophore: str = "Cy3"
    acceptor_fluorophore: str = "Cy5"
    forster_radius_angstrom: float = Field(54.0, ge=10.0, le=100.0)
    acquisition_rate_hz: float = Field(100.0, ge=1.0, le=10000.0)
    traces: Optional[List[TraceInput]] = None


@router.post("/experiments/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_smfret_experiment(
    req: SmFRETAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Analyzes smFRET time-series trajectories, models HMM conformational states, and calculates transition rates."""
    repo = SmFRETRepository(db)

    traces_dict = [t.model_dump() for t in req.traces] if req.traces else None
    eval_res = engine.analyze_experiment(req.model_dump(), traces_dict)

    exp = await repo.create_experiment(
        experiment_title=eval_res["experiment_title"],
        macromolecule_name=eval_res["macromolecule_name"],
        donor_fluorophore=eval_res["donor_fluorophore"],
        acceptor_fluorophore=eval_res["acceptor_fluorophore"],
        forster_radius_angstrom=eval_res["forster_radius_angstrom"],
        acquisition_rate_hz=eval_res["acquisition_rate_hz"],
        total_molecules_recorded=eval_res["total_molecules_recorded"],
        state_count=eval_res["state_count"],
        experiment_metadata_json=eval_res["experiment_metadata_json"],
    )

    created_states = await repo.add_states(exp.id, eval_res["states"])
    created_traces = await repo.add_traces(exp.id, eval_res["traces"])

    return {
        "id": exp.id,
        "experiment_title": exp.experiment_title,
        "macromolecule_name": exp.macromolecule_name,
        "donor_fluorophore": exp.donor_fluorophore,
        "acceptor_fluorophore": exp.acceptor_fluorophore,
        "forster_radius_angstrom": exp.forster_radius_angstrom,
        "acquisition_rate_hz": exp.acquisition_rate_hz,
        "metadata": exp.experiment_metadata_json,
        "states": [
            {
                "state_index": s.state_index,
                "state_name": s.state_name,
                "mean_efficiency": s.mean_efficiency,
                "occupancy_fraction": s.occupancy_fraction,
                "mean_dwell_time_ms": s.mean_dwell_time_ms,
                "transition_rates": s.transition_rates_json,
            }
            for s in created_states
        ],
        "traces": [
            {
                "id": t.id,
                "molecule_index": t.molecule_index,
                "total_frames": t.total_frames,
                "mean_fret_efficiency": t.mean_fret_efficiency,
                "trace_preview_points": len(t.trace_data_json),
            }
            for t in created_traces
        ]
    }


@router.get("/experiments")
async def list_experiments(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists smFRET experiments."""
    repo = SmFRETRepository(db)
    experiments = await repo.list_experiments(limit=limit, offset=offset)
    return [
        {
            "id": e.id,
            "experiment_title": e.experiment_title,
            "macromolecule_name": e.macromolecule_name,
            "donor_fluorophore": e.donor_fluorophore,
            "acceptor_fluorophore": e.acceptor_fluorophore,
            "total_molecules_recorded": e.total_molecules_recorded,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in experiments
    ]


@router.get("/experiments/{experiment_id}")
async def get_experiment_details(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Gets detailed smFRET experiment with HMM states and single-molecule traces."""
    repo = SmFRETRepository(db)
    exp = await repo.get_experiment(experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail="smFRET experiment not found")

    states = await repo.get_states_by_experiment(experiment_id)
    traces = await repo.get_traces_by_experiment(experiment_id)

    return {
        "id": exp.id,
        "experiment_title": exp.experiment_title,
        "macromolecule_name": exp.macromolecule_name,
        "donor_fluorophore": exp.donor_fluorophore,
        "acceptor_fluorophore": exp.acceptor_fluorophore,
        "forster_radius_angstrom": exp.forster_radius_angstrom,
        "acquisition_rate_hz": exp.acquisition_rate_hz,
        "metadata": exp.experiment_metadata_json,
        "states": [
            {
                "id": s.id,
                "state_index": s.state_index,
                "state_name": s.state_name,
                "mean_efficiency": s.mean_efficiency,
                "occupancy_fraction": s.occupancy_fraction,
                "mean_dwell_time_ms": s.mean_dwell_time_ms,
                "transition_rates": s.transition_rates_json,
            }
            for s in states
        ],
        "traces": [
            {
                "id": t.id,
                "molecule_index": t.molecule_index,
                "total_frames": t.total_frames,
                "mean_fret_efficiency": t.mean_fret_efficiency,
                "photobleaching_frame": t.photobleaching_frame,
                "trace_data": t.trace_data_json,
            }
            for t in traces
        ]
    }
