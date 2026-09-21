"""BGC Routes (Phase 123)."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from database.repositories.bgc_mining_repo import BGCRepository
from research.natural_products.bgc_engine import BGCMiningEngine

router = APIRouter(prefix="/bgc-mining", tags=["BGC Mining Engine"])

class BGCMiningRequest(BaseModel):
    organism_species_name: str = Field(..., example="Streptomyces coelicolor A3(2)")
    genome_size_mbp: float = Field(default=8.66, example=8.66)
    workspace_id: Optional[str] = None

@router.post("/mine-genome", status_code=status.HTTP_201_CREATED)
async def mine_bgc_endpoint(req: BGCMiningRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    engine = BGCMiningEngine()
    res = engine.mine_bgcs(req.organism_species_name, req.genome_size_mbp)
    repo = BGCRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else uuid.uuid4()
    g = await repo.create_genome(
        workspace_id=ws_id,
        organism_species_name=res["species"],
        genome_size_mbp=res["genome_size_mbp"],
        total_detected_bgcs=res["total_bgcs"],
        novel_scaffold_fraction=res["novel_fraction"]
    )
    for c in res["clusters"]:
        await repo.add_cluster(
            genome_id=g.id,
            bgc_type=c["type"],
            core_synthetase_genes=c["genes"],
            predicted_chemical_class=c["class"],
            mibiig_known_homology_pct=c["homology"]
        )
    return {"status": "SUCCESS", "genome_id": str(g.id), "result": res}

@router.get("/genomes/{genome_id}")
async def get_genome(genome_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    repo = BGCRepository(db)
    try:
        gid = uuid.UUID(genome_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
    g = await repo.get_genome(gid)
    if not g:
        raise HTTPException(status_code=404, detail="Genome not found")
    return {"id": str(g.id), "species": g.organism_species_name}
