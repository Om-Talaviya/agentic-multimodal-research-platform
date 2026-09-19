"""API Routes for Cryo-EM Protein Flexible Backbone Ensemble Generator (Phase 97)."""

import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.cryo_ensemble_repo import CryoEnsembleRepository
from research.structural.cryo_ensemble_engine import CryoEnsembleEngine

router = APIRouter(prefix="/cryo-ensemble", tags=["Cryo-EM Flexible Backbone Ensemble"])


class CryoEnsembleRequest(BaseModel):
    target_protein: str = Field(..., example="GLP-1R / G-protein Complex")
    pdb_reference_id: str = Field(..., example="7EVM")
    density_map_resolution_angstrom: float = Field(default=2.65, example=2.65)
    num_states: int = Field(default=4, example=4)
    workspace_id: Optional[str] = None


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_cryo_ensemble(
    request: CryoEnsembleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Reconstruct 3D continuous conformational ensemble and Markov state transition barriers."""
    engine = CryoEnsembleEngine()
    result = engine.generate_ensemble_landscape(
        target_protein=request.target_protein,
        pdb_reference_id=request.pdb_reference_id,
        density_map_resolution_angstrom=request.density_map_resolution_angstrom,
        num_states=request.num_states,
    )

    repo = CryoEnsembleRepository(db)
    ws_id = uuid.UUID(request.workspace_id) if request.workspace_id else uuid.uuid4()

    ens = await repo.create_ensemble(
        workspace_id=ws_id,
        target_protein=result["target_protein"],
        pdb_reference_id=result["pdb_reference_id"],
        density_map_resolution_angstrom=result["density_map_resolution_angstrom"],
        latent_space_dimensions=result["latent_space_dimensions"],
        total_conformational_states=result["total_conformational_states"],
        flexibility_rmsd_angstrom=result["flexibility_rmsd_angstrom"],
        ensemble_metadata={"summary": result["summary"]},
    )

    for st in result["states"]:
        await repo.add_state(
            ensemble_id=ens.id,
            state_label=st["label"],
            population_percentage=st["population_percentage"],
            relative_free_energy_kcal_mol=st["relative_free_energy_kcal_mol"],
            backbone_rmsd_to_reference=st["backbone_rmsd_to_reference"],
            binding_pocket_volume_angstrom3=st["binding_pocket_volume_angstrom3"],
        )

    for tr in result["transitions"]:
        await repo.add_transition(
            ensemble_id=ens.id,
            from_state=tr["from_state"],
            to_state=tr["to_state"],
            energy_barrier_kcal_mol=tr["energy_barrier_kcal_mol"],
            transition_rate_per_sec=tr["transition_rate_per_sec"],
        )

    return {
        "status": "SUCCESS",
        "ensemble_id": str(ens.id),
        "target_protein": ens.target_protein,
        "pdb_reference_id": ens.pdb_reference_id,
        "flexibility_rmsd_angstrom": ens.flexibility_rmsd_angstrom,
        "states": result["states"],
        "transitions": result["transitions"],
        "summary": result["summary"],
    }


@router.get("/ensembles/{ensemble_id}")
async def get_ensemble_details(
    ensemble_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Retrieve full Cryo-EM conformational ensemble and transition states."""
    repo = CryoEnsembleRepository(db)
    try:
        eid = uuid.UUID(ensemble_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ensemble UUID format")

    ens = await repo.get_ensemble(eid)
    if not ens:
        raise HTTPException(status_code=404, detail="Cryo-EM ensemble not found")

    return {
        "id": str(ens.id),
        "target_protein": ens.target_protein,
        "pdb_reference_id": ens.pdb_reference_id,
        "density_map_resolution_angstrom": ens.density_map_resolution_angstrom,
        "flexibility_rmsd_angstrom": ens.flexibility_rmsd_angstrom,
        "states": [
            {
                "state_label": s.state_label,
                "population_percentage": s.population_percentage,
                "relative_free_energy_kcal_mol": s.relative_free_energy_kcal_mol,
                "backbone_rmsd_to_reference": s.backbone_rmsd_to_reference,
            }
            for s in ens.states
        ],
        "transitions": [
            {
                "from_state": t.from_state,
                "to_state": t.to_state,
                "energy_barrier_kcal_mol": t.energy_barrier_kcal_mol,
            }
            for t in ens.transitions
        ],
    }
