"""Multiome Routes (Phase 120)."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from database.repositories.multiome_joint_repo import MultiomeRepository
from research.genomics.multiome_engine import SingleCellMultiomeEngine

router = APIRouter(prefix="/multiome-joint", tags=["Multiome Joint Embedding Engine"])

class MultiomeRequest(BaseModel):
    sample_identifier: str = Field(..., example="PBMC_10k_Multiome_ATAC_RNA")
    total_cells: int = Field(default=12400, example=12400)
    workspace_id: Optional[str] = None

@router.post("/embed", status_code=status.HTTP_201_CREATED)
async def embed_multiome_endpoint(req: MultiomeRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    engine = SingleCellMultiomeEngine()
    res = engine.joint_embed_multiome(req.sample_identifier, req.total_cells)
    repo = MultiomeRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else uuid.uuid4()
    ds = await repo.create_dataset(
        workspace_id=ws_id,
        sample_identifier=res["sample_id"],
        total_joint_cells=res["cells"],
        wnn_modality_weight_rna=res["rna_weight"],
        wnn_modality_weight_atac=res["atac_weight"]
    )
    for l in res["linkages"]:
        await repo.add_linkage(
            dataset_id=ds.id,
            target_gene=l["gene"],
            accessible_peak_locus=l["peak"],
            peak_to_gene_correlation=l["corr"],
            binding_transcription_factor=l["tf"]
        )
    return {"status": "SUCCESS", "dataset_id": str(ds.id), "result": res}

@router.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    repo = MultiomeRepository(db)
    try:
        did = uuid.UUID(dataset_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
    d = await repo.get_dataset(did)
    if not d:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"id": str(d.id), "sample": d.sample_identifier}
