"""Cryo Manifold Routes (Phase 117)."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from database.repositories.cryo_dynamic_manifold_repo import CryoManifoldRepository
from research.structural.cryo_manifold_engine import CryoDynamicManifoldEngine

router = APIRouter(prefix="/cryo-manifold", tags=["Cryo Manifold Engine"])

class ManifoldRequest(BaseModel):
    target_complex_name: str = Field(..., example="Spliceosome C Complex")
    total_particles: int = Field(default=145000, example=145000)
    latent_dimensions: int = Field(default=10, example=10)
    workspace_id: Optional[str] = None

@router.post("/embed", status_code=status.HTTP_201_CREATED)
async def embed_manifold_endpoint(req: ManifoldRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    engine = CryoDynamicManifoldEngine()
    res = engine.embed_manifold(req.target_complex_name, req.total_particles, req.latent_dimensions)
    repo = CryoManifoldRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else uuid.uuid4()
    ds = await repo.create_dataset(
        workspace_id=ws_id,
        target_complex_name=res["target"],
        latent_dimensions=res["latent_dimensions"],
        total_particles_aligned=res["particles"],
        manifold_energy_barrier_kcal=res["energy_barrier_kcal"]
    )
    for s in res["states"]:
        await repo.add_state(
            dataset_id=ds.id,
            state_label=s["label"],
            rmsd_from_ground_state=s["rmsd"],
            relative_population_percentage=s["pop"],
            free_energy_delta_kcal=s["dg"]
        )
    return {"status": "SUCCESS", "dataset_id": str(ds.id), "result": res}

@router.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    repo = CryoManifoldRepository(db)
    try:
        did = uuid.UUID(dataset_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
    d = await repo.get_dataset(did)
    if not d:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"id": str(d.id), "target": d.target_complex_name}
