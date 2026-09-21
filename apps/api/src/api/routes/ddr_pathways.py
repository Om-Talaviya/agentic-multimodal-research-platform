"""DDR Routes (Phase 119)."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from database.repositories.ddr_pathways_repo import DDRPathwayRepository
from research.oncology.ddr_engine import DDRPathwayEngine

router = APIRouter(prefix="/ddr-pathways", tags=["DDR Pathways Engine"])

class DDRAnalysisRequest(BaseModel):
    cancer_type: str = Field(..., example="High-Grade Serous Ovarian Cancer")
    primary_ddr_defect: str = Field(default="BRCA1 Germline Truncation", example="BRCA1 Germline Truncation")
    hrd_genomic_scar_score: float = Field(default=64.0, example=64.0)
    workspace_id: Optional[str] = None

@router.post("/model-vulnerabilities", status_code=status.HTTP_201_CREATED)
async def model_ddr_endpoint(req: DDRAnalysisRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    engine = DDRPathwayEngine()
    res = engine.model_ddr_synthetic_lethality(req.cancer_type, req.primary_ddr_defect, req.hrd_genomic_scar_score)
    repo = DDRPathwayRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else uuid.uuid4()
    p = await repo.create_profile(
        workspace_id=ws_id,
        cancer_type=res["cancer_type"],
        primary_ddr_defect=res["primary_defect"],
        hrd_genomic_scar_score=res["hrd_score"],
        replication_stress_index=res["replication_stress"]
    )
    for t in res["targets"]:
        await repo.add_interaction(
            ddr_profile_id=p.id,
            therapeutic_target_gene=t["gene"],
            synthetic_lethal_potency_score=t["potency"],
            recommended_inhibitor_class=t["drug"]
        )
    return {"status": "SUCCESS", "profile_id": str(p.id), "result": res}

@router.get("/profiles/{profile_id}")
async def get_profile(profile_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    repo = DDRPathwayRepository(db)
    try:
        pid = uuid.UUID(profile_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
    p = await repo.get_profile(pid)
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"id": str(p.id), "cancer": p.cancer_type}
