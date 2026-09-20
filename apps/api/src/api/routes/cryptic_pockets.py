"""
FastAPI route for Phase 107: Allosteric Pocket Discovery & Cryptic Binding Site Mapper.
"""
import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from database.repositories.cryptic_pockets_repo import CrypticPocketRepository
from research.structural.cryptic_pocket_engine import CrypticPocketEngine

router = APIRouter(prefix="/cryptic-pockets", tags=["Phase 107: Allosteric & Cryptic Pockets"])

class CandidatePocketInput(BaseModel):
    pocket_name: str
    center_x: float = 0.0
    center_y: float = 0.0
    center_z: float = 0.0
    apo_volume_a3: float
    holo_volume_a3: float
    hydrophobicity_score: float = 0.75
    enclosing_residues: Optional[str] = None

class CrypticDiscoveryRequest(BaseModel):
    target_protein: str
    pdb_id: Optional[str] = None
    trajectory_frames_sampled: int = Field(default=100, ge=10, le=1000)
    candidate_pockets: Optional[List[CandidatePocketInput]] = None

class AllostericPocketResponse(BaseModel):
    pocket_name: str
    center_x: float
    center_y: float
    center_z: float
    apo_volume_a3: float
    holo_volume_a3: float
    volume_expansion_ratio: float
    druggability_index: float
    hydrophobicity_score: float
    enclosing_residues: Optional[str] = None

class CoupledNetworkResponse(BaseModel):
    source_residue: str
    target_residue: str
    allosteric_correlation: float
    pathway_shortest_distance_a: float

class CrypticAnalysisResponse(BaseModel):
    id: str
    target_protein: str
    pdb_id: Optional[str] = None
    trajectory_frames_sampled: int
    detected_cryptic_pockets: int
    max_druggability_score: float
    allosteric_coupling_score: float
    status: str
    pockets: List[Dict[str, Any]] = []
    coupled_networks: List[Dict[str, Any]] = []

@router.post("/discover", response_model=CrypticAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def discover_cryptic_pockets(
    request: CrypticDiscoveryRequest,
    db: AsyncSession = Depends(get_db)
):
    engine = CrypticPocketEngine()
    raw_pockets = [p.model_dump() for p in request.candidate_pockets] if request.candidate_pockets else None
    discovery = engine.discover_cryptic_pockets(
        target_protein=request.target_protein,
        pdb_id=request.pdb_id,
        trajectory_frames_sampled=request.trajectory_frames_sampled,
        candidate_pockets=raw_pockets
    )

    repo = CrypticPocketRepository(db)
    analysis = await repo.create_analysis(
        target_protein=discovery["target_protein"],
        pdb_id=discovery["pdb_id"],
        trajectory_frames_sampled=discovery["trajectory_frames_sampled"],
        max_druggability_score=discovery["max_druggability_score"],
        allosteric_coupling_score=discovery["allosteric_coupling_score"]
    )

    await repo.add_pockets(analysis.id, discovery["pockets"])
    await repo.add_coupled_networks(analysis.id, discovery["coupled_networks"])

    hydrated = await repo.get_analysis(analysis.id)
    if not hydrated:
        raise HTTPException(status_code=500, detail="Failed to retrieve cryptic pocket analysis")

    return CrypticAnalysisResponse(
        id=str(hydrated.id),
        target_protein=hydrated.target_protein,
        pdb_id=hydrated.pdb_id,
        trajectory_frames_sampled=hydrated.trajectory_frames_sampled,
        detected_cryptic_pockets=hydrated.detected_cryptic_pockets,
        max_druggability_score=hydrated.max_druggability_score,
        allosteric_coupling_score=hydrated.allosteric_coupling_score,
        status=hydrated.status,
        pockets=[{
            "pocket_name": p.pocket_name,
            "center_x": p.center_x,
            "center_y": p.center_y,
            "center_z": p.center_z,
            "apo_volume_a3": p.apo_volume_a3,
            "holo_volume_a3": p.holo_volume_a3,
            "volume_expansion_ratio": p.volume_expansion_ratio,
            "druggability_index": p.druggability_index,
            "hydrophobicity_score": p.hydrophobicity_score,
            "enclosing_residues": p.enclosing_residues
        } for p in hydrated.pockets],
        coupled_networks=[{
            "source_residue": n.source_residue,
            "target_residue": n.target_residue,
            "allosteric_correlation": n.allosteric_correlation,
            "pathway_shortest_distance_a": n.pathway_shortest_distance_a
        } for n in hydrated.coupled_networks]
    )

@router.get("/analyses", response_model=List[CrypticAnalysisResponse])
async def list_cryptic_analyses(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    repo = CrypticPocketRepository(db)
    analyses = await repo.list_analyses(limit=limit, offset=offset)
    return [
        CrypticAnalysisResponse(
            id=str(a.id),
            target_protein=a.target_protein,
            pdb_id=a.pdb_id,
            trajectory_frames_sampled=a.trajectory_frames_sampled,
            detected_cryptic_pockets=a.detected_cryptic_pockets,
            max_druggability_score=a.max_druggability_score,
            allosteric_coupling_score=a.allosteric_coupling_score,
            status=a.status,
            pockets=[],
            coupled_networks=[]
        )
        for a in analyses
    ]

@router.get("/analyses/{analysis_id}", response_model=CrypticAnalysisResponse)
async def get_cryptic_analysis_detail(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    repo = CrypticPocketRepository(db)
    hydrated = await repo.get_analysis(analysis_id)
    if not hydrated:
        raise HTTPException(status_code=404, detail="Cryptic pocket analysis not found")

    return CrypticAnalysisResponse(
        id=str(hydrated.id),
        target_protein=hydrated.target_protein,
        pdb_id=hydrated.pdb_id,
        trajectory_frames_sampled=hydrated.trajectory_frames_sampled,
        detected_cryptic_pockets=hydrated.detected_cryptic_pockets,
        max_druggability_score=hydrated.max_druggability_score,
        allosteric_coupling_score=hydrated.allosteric_coupling_score,
        status=hydrated.status,
        pockets=[{
            "pocket_name": p.pocket_name,
            "center_x": p.center_x,
            "center_y": p.center_y,
            "center_z": p.center_z,
            "apo_volume_a3": p.apo_volume_a3,
            "holo_volume_a3": p.holo_volume_a3,
            "volume_expansion_ratio": p.volume_expansion_ratio,
            "druggability_index": p.druggability_index,
            "hydrophobicity_score": p.hydrophobicity_score,
            "enclosing_residues": p.enclosing_residues
        } for p in hydrated.pockets],
        coupled_networks=[{
            "source_residue": n.source_residue,
            "target_residue": n.target_residue,
            "allosteric_correlation": n.allosteric_correlation,
            "pathway_shortest_distance_a": n.pathway_shortest_distance_a
        } for n in hydrated.coupled_networks]
    )
