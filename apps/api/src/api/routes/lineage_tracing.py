"""Lineage Routes (Phase 114)."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from database.repositories.lineage_tracing_repo import LineageTracingRepository
from research.genomics.lineage_engine import LineageTracingEngine

router = APIRouter(prefix="/lineage-tracing", tags=["Lineage Tracing Engine"])

class LineageAnalysisRequest(BaseModel):
    experiment_title: str = Field(..., example="Chemotherapy Resistance Clonal Evolution")
    barcoding_technology: str = Field(default="CRISPR-Cas9 Scarring (GESTALT)", example="CRISPR-Cas9 Scarring (GESTALT)")
    total_clones: int = Field(default=850, example=850)
    selection_pressure: str = Field(default="Cisplatin 10uM Selection", example="Cisplatin 10uM Selection")
    workspace_id: Optional[str] = None

@router.post("/simulate", status_code=status.HTTP_201_CREATED)
async def simulate_lineage_endpoint(req: LineageAnalysisRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    engine = LineageTracingEngine()
    res = engine.simulate_clonal_trajectories(req.experiment_title, req.barcoding_technology, req.total_clones, req.selection_pressure)
    repo = LineageTracingRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else uuid.uuid4()
    exp = await repo.create_experiment(
        workspace_id=ws_id,
        experiment_title=res["title"],
        barcoding_technology=res["technology"],
        total_unique_clones=res["total_clones"],
        shannon_entropy_diversity=res["shannon_entropy"],
        dominant_clone_fraction=res["dominant_clone_fraction"]
    )
    for c in res["top_clones"]:
        await repo.add_trajectory(
            experiment_id=exp.id,
            clone_barcode_id=c["barcode"],
            initial_frequency=c["init_freq"],
            post_selection_frequency=c["post_freq"],
            relative_fitness_coefficient=c["fitness"],
            resistance_conferring_driver=c["driver"]
        )
    return {"status": "SUCCESS", "experiment_id": str(exp.id), "result": res}

@router.get("/experiments/{experiment_id}")
async def get_lineage_experiment(experiment_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    repo = LineageTracingRepository(db)
    try:
        eid = uuid.UUID(experiment_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
    e = await repo.get_experiment(eid)
    if not e:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return {"id": str(e.id), "title": e.experiment_title}
