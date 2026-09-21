"""CTC Routes (Phase 111)."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from database.repositories.ctc_metastasis_repo import CTCRepository
from research.cancer_biology.ctc_engine import CTCTrajectoryEngine

router = APIRouter(prefix="/ctc-metastasis", tags=["CTC Metastasis Engine"])

class CTCAnalysisRequest(BaseModel):
    patient_id: str = Field(..., example="PT-MET-8841")
    primary_tumor_type: str = Field(..., example="Triple-Negative Breast Cancer")
    ctc_count: int = Field(default=22, example=22)
    epcam_expression: float = Field(default=1.2, example=1.2)
    vimentin_expression: float = Field(default=3.8, example=3.8)
    workspace_id: Optional[str] = None

@router.post("/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_ctc_sample(req: CTCAnalysisRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    engine = CTCTrajectoryEngine()
    res = engine.analyze_ctc_trajectory(req.patient_id, req.primary_tumor_type, req.ctc_count, req.epcam_expression, req.vimentin_expression)
    repo = CTCRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else uuid.uuid4()
    sample = await repo.create_sample(
        workspace_id=ws_id,
        patient_id=res["patient_id"],
        primary_tumor_type=res["primary_tumor_type"],
        ctc_enumeration_per_7_5ml=res["ctc_enumeration_per_7_5ml"],
        emt_hybrid_score=res["emt_hybrid_score"],
        metastatic_tropism_primary=res["dominant_tropism"]
    )
    for s in res["colonization_sites"]:
        await repo.add_colonization_site(
            ctc_sample_id=sample.id,
            target_organ=s["target_organ"],
            colonization_probability=s["colonization_probability"],
            seed_soil_compatibility_score=s["seed_soil_compatibility"],
            chemokine_gradient_strength=s["chemokine_gradient"]
        )
    return {"status": "SUCCESS", "sample_id": str(sample.id), "result": res}

@router.get("/samples/{sample_id}")
async def get_ctc_sample(sample_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    repo = CTCRepository(db)
    try:
        sid = uuid.UUID(sample_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
    s = await repo.get_sample(sid)
    if not s:
        raise HTTPException(status_code=404, detail="Sample not found")
    return {"id": str(s.id), "patient_id": s.patient_id, "primary_tumor_type": s.primary_tumor_type, "emt_hybrid_score": s.emt_hybrid_score}
