"""TCE Routes (Phase 113)."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from database.repositories.tce_bispecific_repo import TCERepository
from research.immunotherapy.tce_engine import TCEGeometryEngine

router = APIRouter(prefix="/tce-bispecific", tags=["TCE Bispecific Optimizer"])

class TCEOptimizationRequest(BaseModel):
    construct_name: str = Field(..., example="Anti-HER2xCD3_BiTE_v2")
    tumor_target_antigen: str = Field(..., example="HER2 (ErbB2)")
    format_geometry: str = Field(default="BiTE (scFv-scFv)", example="BiTE (scFv-scFv)")
    linker_length_aa: int = Field(default=15, example=15)
    workspace_id: Optional[str] = None

@router.post("/optimize", status_code=status.HTTP_201_CREATED)
async def optimize_tce_endpoint(req: TCEOptimizationRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    engine = TCEGeometryEngine()
    res = engine.optimize_tce_geometry(req.construct_name, req.tumor_target_antigen, req.format_geometry, req.linker_length_aa)
    repo = TCERepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else uuid.uuid4()
    construct = await repo.create_construct(
        workspace_id=ws_id,
        construct_name=res["construct_name"],
        tumor_target_antigen=res["tumor_target_antigen"],
        tcell_effector_arm="Anti-CD3e UCHT1",
        format_geometry=res["format_geometry"],
        linker_length_amino_acids=res["linker_length_aa"],
        synapse_distance_angstroms=res["synapse_distance_angstroms"],
        cytotoxicity_ec50_pm=res["cytotoxicity_ec50_pm"],
        crs_safety_index=res["crs_safety_index"]
    )
    await repo.add_synapse_metric(
        construct_id=construct.id,
        intermembrane_distance_nm=res["intermembrane_distance_nm"],
        cd45_exclusion_efficiency=res["cd45_exclusion_efficiency"],
        perforin_granzyme_flux_score=res["perforin_granzyme_flux_score"]
    )
    return {"status": "SUCCESS", "construct_id": str(construct.id), "result": res}

@router.get("/constructs/{construct_id}")
async def get_tce_construct(construct_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    repo = TCERepository(db)
    try:
        cid = uuid.UUID(construct_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
    c = await repo.get_construct(cid)
    if not c:
        raise HTTPException(status_code=404, detail="Construct not found")
    return {"id": str(c.id), "construct_name": c.construct_name}
