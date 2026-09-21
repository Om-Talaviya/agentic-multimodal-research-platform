"""Spatial MSI Routes (Phase 116)."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from database.repositories.spatial_metabolite_imaging_repo import SpatialMSIRepository
from research.spatial.metabolite_imaging_engine import SpatialMetaboliteImagingEngine

router = APIRouter(prefix="/spatial-msi", tags=["Spatial MSI Engine"])

class MSIAnalysisRequest(BaseModel):
    tissue_section_name: str = Field(..., example="Glioblastoma_Tissue_Slice_04")
    msi_modality: str = Field(default="MALDI-MSI (FT-ICR)", example="MALDI-MSI (FT-ICR)")
    spatial_resolution_um: float = Field(default=20.0, example=20.0)
    workspace_id: Optional[str] = None

@router.post("/profile-gradients", status_code=status.HTTP_201_CREATED)
async def profile_msi_endpoint(req: MSIAnalysisRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    engine = SpatialMetaboliteImagingEngine()
    res = engine.profile_metabolite_gradients(req.tissue_section_name, req.msi_modality, req.spatial_resolution_um)
    repo = SpatialMSIRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else uuid.uuid4()
    sample = await repo.create_sample(
        workspace_id=ws_id,
        tissue_section_name=res["tissue_section_name"],
        msi_modality=res["msi_modality"],
        spatial_resolution_microns=res["spatial_resolution_microns"],
        total_mz_features=res["total_mz_features"],
        warburg_lactate_gradient_ratio=res["warburg_lactate_ratio"]
    )
    for g in res["gradients"]:
        await repo.add_gradient(
            msi_sample_id=sample.id,
            metabolite_name=g["metabolite"],
            mz_ratio=g["mz"],
            tumor_core_intensity=g["tumor_core_intensity"],
            stromal_border_intensity=g["border_intensity"],
            core_to_border_ratio=g["gradient_ratio"]
        )
    return {"status": "SUCCESS", "sample_id": str(sample.id), "result": res}

@router.get("/samples/{sample_id}")
async def get_msi_sample(sample_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    repo = SpatialMSIRepository(db)
    try:
        sid = uuid.UUID(sample_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
    s = await repo.get_sample(sid)
    if not s:
        raise HTTPException(status_code=404, detail="Sample not found")
    return {"id": str(s.id), "tissue": s.tissue_section_name}
