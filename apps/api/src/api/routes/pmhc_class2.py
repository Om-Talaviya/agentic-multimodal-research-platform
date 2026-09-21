"""MHC Class II Routes (Phase 118)."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from database.repositories.pmhc_class2_repo import MHCClass2Repository
from research.immunology.pmhc_class2_engine import PMHCClass2Engine

router = APIRouter(prefix="/pmhc-class2", tags=["pMHC Class II Engine"])

class Class2ScreenRequest(BaseModel):
    hla_class2_allele: str = Field(..., example="HLA-DRB1*04:01")
    source_protein_antigen: str = Field(..., example="NY-ESO-1 (CTAG1B)")
    protein_sequence: str = Field(default="MQAEGRGT...", example="MQAEGRGT...")
    workspace_id: Optional[str] = None

@router.post("/predict-neoepitopes", status_code=status.HTTP_201_CREATED)
async def predict_class2_endpoint(req: Class2ScreenRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    engine = PMHCClass2Engine()
    res = engine.predict_class2_neoepitopes(req.hla_class2_allele, req.source_protein_antigen, req.protein_sequence)
    repo = MHCClass2Repository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else uuid.uuid4()
    screen = await repo.create_screen(
        workspace_id=ws_id,
        hla_class2_allele=res["allele"],
        source_protein_antigen=res["antigen"],
        total_screened_15mers=res["screened_peptides"],
        immunogenic_hits_count=res["hits_count"]
    )
    for h in res["hits"]:
        await repo.add_neoepitope(
            screen_id=screen.id,
            peptide_15mer_sequence=h["peptide"],
            core_9mer_binding_motif=h["core"],
            binding_affinity_ic50_nm=h["ic50"],
            cd4_immunogenicity_tier=h["tier"]
        )
    return {"status": "SUCCESS", "screen_id": str(screen.id), "result": res}

@router.get("/screens/{screen_id}")
async def get_screen(screen_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    repo = MHCClass2Repository(db)
    try:
        sid = uuid.UUID(screen_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
    s = await repo.get_screen(sid)
    if not s:
        raise HTTPException(status_code=404, detail="Screen not found")
    return {"id": str(s.id), "allele": s.hla_class2_allele}
