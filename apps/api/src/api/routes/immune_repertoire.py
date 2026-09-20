"""
FastAPI route for Phase 104: Single-Cell TCR/BCR Clonotype & Immune Repertoire Analysis.
"""
import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from database.repositories.immune_repertoire_repo import ImmuneRepertoireRepository
from research.immunology.tcr_clonotype_engine import TCRClonotypeEngine

router = APIRouter(prefix="/immune-repertoire", tags=["Phase 104: Immune Repertoire"])

class ClonotypeInput(BaseModel):
    cdr3_aa: str
    v_gene: str
    j_gene: str
    cdr3_nt: Optional[str] = None
    d_gene: Optional[str] = None
    c_gene: Optional[str] = None
    count: int = Field(default=1, ge=1)
    is_productive: bool = True

class RepertoireAnalysisRequest(BaseModel):
    sample_name: str
    organism: str = "Homo sapiens"
    chain_type: str = "TCR_ALPHA_BETA"
    clonotypes: List[ClonotypeInput]

class ClonotypeResponse(BaseModel):
    id: str
    cdr3_aa: str
    v_gene: str
    j_gene: str
    frequency: float
    count: int
    antigen_specificity: Optional[str] = None

class VDJPairingResponse(BaseModel):
    v_family: str
    j_family: str
    pairing_frequency: float
    cdr3_length: int

class RepertoireResponse(BaseModel):
    id: str
    sample_name: str
    organism: str
    chain_type: str
    clonotype_count: int
    total_cells: int
    shannon_entropy: float
    gini_simpson_index: float
    clonality_score: float
    status: str
    clonotypes: List[Dict[str, Any]] = []
    vdj_pairings: List[Dict[str, Any]] = []

@router.post("/analyze", response_model=RepertoireResponse, status_code=status.HTTP_201_CREATED)
async def analyze_and_store_repertoire(
    request: RepertoireAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    engine = TCRClonotypeEngine()
    raw_data = [c.model_dump() for c in request.clonotypes]
    analysis = engine.analyze_repertoire(
        sample_name=request.sample_name,
        raw_clonotypes=raw_data,
        organism=request.organism,
        chain_type=request.chain_type
    )

    repo = ImmuneRepertoireRepository(db)
    repertoire = await repo.create_repertoire(
        sample_name=analysis["sample_name"],
        organism=analysis["organism"],
        chain_type=analysis["chain_type"],
        total_cells=analysis["total_cells"],
        shannon_entropy=analysis["shannon_entropy"],
        gini_simpson_index=analysis["gini_simpson_index"],
        clonality_score=analysis["clonality_score"]
    )

    await repo.add_clonotypes(repertoire.id, analysis["clonotypes"])
    await repo.add_vdj_pairings(repertoire.id, analysis["vdj_pairings"])

    hydrated = await repo.get_repertoire(repertoire.id)
    if not hydrated:
        raise HTTPException(status_code=500, detail="Failed to retrieve persisted repertoire")

    return RepertoireResponse(
        id=str(hydrated.id),
        sample_name=hydrated.sample_name,
        organism=hydrated.organism,
        chain_type=hydrated.chain_type,
        clonotype_count=hydrated.clonotype_count,
        total_cells=hydrated.total_cells,
        shannon_entropy=hydrated.shannon_entropy,
        gini_simpson_index=hydrated.gini_simpson_index,
        clonality_score=hydrated.clonality_score,
        status=hydrated.status,
        clonotypes=[{
            "id": str(c.id),
            "cdr3_aa": c.cdr3_aa,
            "v_gene": c.v_gene,
            "j_gene": c.j_gene,
            "frequency": c.frequency,
            "count": c.count,
            "antigen_specificity": c.antigen_specificity
        } for c in hydrated.clonotypes],
        vdj_pairings=[{
            "v_family": p.v_family,
            "j_family": p.j_family,
            "pairing_frequency": p.pairing_frequency,
            "cdr3_length": p.cdr3_length
        } for p in hydrated.vdj_pairings]
    )

@router.get("/repertoires", response_model=List[RepertoireResponse])
async def list_repertoires(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    repo = ImmuneRepertoireRepository(db)
    repertoires = await repo.list_repertoires(limit=limit, offset=offset)
    return [
        RepertoireResponse(
            id=str(r.id),
            sample_name=r.sample_name,
            organism=r.organism,
            chain_type=r.chain_type,
            clonotype_count=r.clonotype_count,
            total_cells=r.total_cells,
            shannon_entropy=r.shannon_entropy,
            gini_simpson_index=r.gini_simpson_index,
            clonality_score=r.clonality_score,
            status=r.status,
            clonotypes=[],
            vdj_pairings=[]
        )
        for r in repertoires
    ]

@router.get("/repertoires/{repertoire_id}", response_model=RepertoireResponse)
async def get_repertoire_detail(
    repertoire_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    repo = ImmuneRepertoireRepository(db)
    hydrated = await repo.get_repertoire(repertoire_id)
    if not hydrated:
        raise HTTPException(status_code=404, detail="Immune repertoire not found")
    
    return RepertoireResponse(
        id=str(hydrated.id),
        sample_name=hydrated.sample_name,
        organism=hydrated.organism,
        chain_type=hydrated.chain_type,
        clonotype_count=hydrated.clonotype_count,
        total_cells=hydrated.total_cells,
        shannon_entropy=hydrated.shannon_entropy,
        gini_simpson_index=hydrated.gini_simpson_index,
        clonality_score=hydrated.clonality_score,
        status=hydrated.status,
        clonotypes=[{
            "id": str(c.id),
            "cdr3_aa": c.cdr3_aa,
            "v_gene": c.v_gene,
            "j_gene": c.j_gene,
            "frequency": c.frequency,
            "count": c.count,
            "antigen_specificity": c.antigen_specificity
        } for c in hydrated.clonotypes],
        vdj_pairings=[{
            "v_family": p.v_family,
            "j_family": p.j_family,
            "pairing_frequency": p.pairing_frequency,
            "cdr3_length": p.cdr3_length
        } for p in hydrated.vdj_pairings]
    )
