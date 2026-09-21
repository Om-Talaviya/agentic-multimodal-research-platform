"""TPD Routes (Phase 121)."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from database.repositories.tpd_molecular_glue_repo import MolecularGlueRepository
from research.pharmacology.tpd_engine import TPDMolecularGlueEngine

router = APIRouter(prefix="/tpd-molecular-glue", tags=["TPD Molecular Glue Engine"])

class GlueScreenRequest(BaseModel):
    e3_ligase_name: str = Field(..., example="CRBN")
    target_neo_substrate: str = Field(..., example="GSPT1 (eRF3a)")
    campaign_name: str = Field(default="AML Degradation Screen 2026", example="AML Degradation Screen 2026")
    workspace_id: Optional[str] = None

@router.post("/screen", status_code=status.HTTP_201_CREATED)
async def screen_glues_endpoint(req: GlueScreenRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    engine = TPDMolecularGlueEngine()
    res = engine.rank_molecular_glues(req.e3_ligase_name, req.target_neo_substrate, req.campaign_name)
    repo = MolecularGlueRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else uuid.uuid4()
    s = await repo.create_screen(
        workspace_id=ws_id,
        e3_ligase_name=res["ligase"],
        target_neo_substrate=res["substrate"],
        screen_campaign_name=res["campaign"],
        total_screened_glues=res["total_glues"],
        top_glue_candidate=res["top_candidate"]
    )
    for g in res["glues"]:
        await repo.add_ternary_affinity(
            screen_id=s.id,
            glue_molecule_smiles=g["smiles"],
            cooperativity_factor_alpha=g["alpha"],
            ternary_kd_apparent_nm=g["kd_nm"],
            dc50_degradation_potency_nm=g["dc50_nm"]
        )
    return {"status": "SUCCESS", "screen_id": str(s.id), "result": res}

@router.get("/screens/{screen_id}")
async def get_screen(screen_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    repo = MolecularGlueRepository(db)
    try:
        sid = uuid.UUID(screen_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
    s = await repo.get_screen(sid)
    if not s:
        raise HTTPException(status_code=404, detail="Screen not found")
    return {"id": str(s.id), "ligase": s.e3_ligase_name}
