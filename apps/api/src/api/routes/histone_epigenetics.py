"""Histone Routes (Phase 112)."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from database.repositories.histone_epigenetics_repo import HistoneEpigeneticsRepository
from research.epigenomics.histone_engine import HistoneEpigeneticsEngine

router = APIRouter(prefix="/histone-epigenetics", tags=["Histone Epigenetics Engine"])

class HistoneChIPRequest(BaseModel):
    sample_name: str = Field(..., example="Jurkat_TCell_H3K27ac")
    histone_mark: str = Field(default="H3K27ac", example="H3K27ac")
    tissue_or_cell_line: str = Field(..., example="T-Cell Acute Lymphoblastic Leukemia")
    total_peaks: int = Field(default=18500, example=18500)
    workspace_id: Optional[str] = None

@router.post("/call-super-enhancers", status_code=status.HTTP_201_CREATED)
async def call_super_enhancers_endpoint(req: HistoneChIPRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    engine = HistoneEpigeneticsEngine()
    res = engine.call_super_enhancers(req.sample_name, req.histone_mark, req.tissue_or_cell_line, req.total_peaks)
    repo = HistoneEpigeneticsRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else uuid.uuid4()
    sample = await repo.create_sample(
        workspace_id=ws_id,
        sample_name=res["sample_name"],
        histone_mark=res["histone_mark"],
        cell_line_or_tissue=res["tissue"],
        total_aligned_peaks=res["total_peaks"],
        super_enhancer_count=res["super_enhancers_called"],
        frip_score=res["frip_score"]
    )
    for se in res["top_enhancers"]:
        await repo.add_super_enhancer(
            chip_sample_id=sample.id,
            locus_coordinates=se["locus"],
            associated_oncogene=se["oncogene"],
            rose_ranking_score=se["rose_score"],
            signal_intensity_rpm=se["signal_intensity_rpm"]
        )
    return {"status": "SUCCESS", "sample_id": str(sample.id), "result": res}

@router.get("/samples/{sample_id}")
async def get_chip_sample(sample_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    repo = HistoneEpigeneticsRepository(db)
    try:
        sid = uuid.UUID(sample_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
    s = await repo.get_sample(sid)
    if not s:
        raise HTTPException(status_code=404, detail="Sample not found")
    return {"id": str(s.id), "sample_name": s.sample_name}
