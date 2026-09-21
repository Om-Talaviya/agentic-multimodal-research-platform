"""miRNA Routes (Phase 115)."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from database.repositories.mirna_regulation_repo import MiRNARepository
from research.rna_biology.mirna_engine import MiRNARegulationEngine

router = APIRouter(prefix="/mirna-regulation", tags=["miRNA Regulation Engine"])

class MiRNAModelingRequest(BaseModel):
    mirna_id: str = Field(..., example="hsa-miR-21-5p")
    seed_sequence: str = Field(default="AGCUUAU", example="AGCUUAU")
    disease_context: str = Field(..., example="Glioblastoma Multiforme")
    workspace_id: Optional[str] = None

@router.post("/model-network", status_code=status.HTTP_201_CREATED)
async def model_mirna_endpoint(req: MiRNAModelingRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    engine = MiRNARegulationEngine()
    res = engine.model_mirna_targets(req.mirna_id, req.seed_sequence, req.disease_context)
    repo = MiRNARepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else uuid.uuid4()
    net = await repo.create_network(
        workspace_id=ws_id,
        mirna_id=res["mirna_id"],
        seed_sequence=res["seed_sequence"],
        disease_context=res["disease_context"],
        total_predicted_targets=res["total_targets_predicted"],
        network_density=res["network_density"]
    )
    for t in res["top_targets"]:
        await repo.add_target(
            network_id=net.id,
            target_gene=t["gene"],
            seed_match_type=t["match"],
            binding_free_energy_kcal_mol=t["energy"],
            predicted_repression_fold=t["repression"]
        )
    return {"status": "SUCCESS", "network_id": str(net.id), "result": res}

@router.get("/networks/{network_id}")
async def get_mirna_network(network_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    repo = MiRNARepository(db)
    try:
        nid = uuid.UUID(network_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
    net = await repo.get_network(nid)
    if not net:
        raise HTTPException(status_code=404, detail="Network not found")
    return {"id": str(net.id), "mirna_id": net.mirna_id}
