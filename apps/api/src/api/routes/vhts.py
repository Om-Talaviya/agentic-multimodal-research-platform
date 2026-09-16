"""
REST API routes for Virtual High-Throughput Screening (vHTS) (Phase 54).
Provides docking campaign initiation, hit filtering, and scaffold cluster analysis.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session
from database.repositories.vhts_repo import VirtualHTSRepository
from research.vhts.vhts_engine import VirtualHTSEngine

router = APIRouter(prefix="/vhts", tags=["Virtual High-Throughput Screening"])
engine = VirtualHTSEngine()


# ---------------------------------------------------------------------------
# Pydantic Request & Response Schemas
# ---------------------------------------------------------------------------

class ScreenCreateRequest(BaseModel):
    target_protein_name: str = Field(..., example="EGFR T790M / C797S Kinase Domain")
    pdb_id: str = Field(..., example="7L11")
    binding_pocket_box: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {"center": [12.4, -4.2, 28.1], "size": [20.0, 20.0, 20.0]}
    )
    library_source: str = Field("Enamine_REAL_10M", example="Enamine_REAL_10M")
    total_screened_compounds: int = Field(1000000, example=1000000)
    candidate_smiles_list: Optional[List[str]] = Field(
        default_factory=lambda: [
            "CC(C)N1CCN(CC1)c2cc3ncccc3nc2Nc4ccc(F)cc4",
            "O=C(Nc1ccc(F)cc1)c2cc3ccccc3[nH]2",
            "NS(=O)(=O)c1ccc(Nc2ncccn2)cc1",
        ]
    )


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@router.post("/screens", status_code=status.HTTP_201_CREATED)
async def create_vhts_screen(
    req: ScreenCreateRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Launch a virtual HTS campaign, evaluate docking poses, and cluster top hits."""
    repo = VirtualHTSRepository(db)

    screen = await repo.create_screen(
        target_protein_name=req.target_protein_name,
        pdb_id=req.pdb_id,
        binding_pocket_box=req.binding_pocket_box,
        library_source=req.library_source,
        total_screened=req.total_screened_compounds,
    )

    evaluated_hits = []
    for idx, smiles in enumerate(req.candidate_smiles_list or []):
        eval_result = engine.evaluate_docking_pose(
            smiles=smiles,
            target_pdb_id=req.pdb_id,
            pocket_box=req.binding_pocket_box or {},
        )
        hit = await repo.add_hit(
            screen_id=screen.id,
            compound_id=f"REAL-CMP-{1000 + idx}",
            smiles=smiles,
            docking_score_kcal_mol=eval_result["docking_score_kcal_mol"],
            cwas_energy=eval_result["cwas_electrostatics"],
            pains_filter_passed=eval_result["pains_filter_passed"],
            rmsd_to_reference=eval_result["rmsd_to_reference"],
            pose_coordinates_json={"kd_nm": eval_result["estimated_kd_nm"]},
        )
        evaluated_hits.append(eval_result)

    # Generate and record scaffold clusters
    clusters = engine.cluster_hits(evaluated_hits)
    for c in clusters:
        await repo.add_cluster(
            screen_id=screen.id,
            cluster_label=c["cluster_label"],
            scaffold_smiles=c["scaffold_smiles"],
            member_hits_count=c["member_hits_count"],
            mean_affinity_kcal_mol=c["mean_affinity_kcal_mol"],
        )

    return await repo.get_screen(screen.id)


@router.get("/screens")
async def list_vhts_screens(
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session),
):
    """List all virtual screening runs."""
    repo = VirtualHTSRepository(db)
    screens = await repo.list_screens(limit=limit)
    response = []
    for s in screens:
        hits = await repo.list_hits(s.id, limit=5)
        clusters = await repo.list_clusters(s.id)
        response.append({
            "id": s.id,
            "target_protein_name": s.target_protein_name,
            "pdb_id": s.pdb_id,
            "library_source": s.library_source,
            "total_screened_compounds": s.total_screened_compounds,
            "top_hits_count": s.top_hits_count,
            "best_affinity_kcal_mol": s.best_affinity_kcal_mol,
            "status": s.status,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "top_hits": [
                {
                    "compound_id": h.compound_id,
                    "smiles": h.smiles,
                    "docking_score": h.docking_score_kcal_mol,
                    "pains_passed": h.pains_filter_passed,
                }
                for h in hits
            ],
            "clusters_count": len(clusters),
        })
    return response


@router.get("/screens/{screen_id}")
async def get_vhts_screen(
    screen_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get screen details with hits and scaffold clusters."""
    repo = VirtualHTSRepository(db)
    screen = await repo.get_screen(screen_id)
    if not screen:
        raise HTTPException(status_code=404, detail="vHTS screen not found.")

    hits = await repo.list_hits(screen_id)
    clusters = await repo.list_clusters(screen_id)

    return {
        "id": screen.id,
        "target_protein_name": screen.target_protein_name,
        "pdb_id": screen.pdb_id,
        "binding_pocket_box": screen.binding_pocket_box,
        "library_source": screen.library_source,
        "total_screened_compounds": screen.total_screened_compounds,
        "top_hits_count": screen.top_hits_count,
        "best_affinity_kcal_mol": screen.best_affinity_kcal_mol,
        "status": screen.status,
        "created_at": screen.created_at.isoformat() if screen.created_at else None,
        "hits": [
            {
                "id": h.id,
                "compound_id": h.compound_id,
                "smiles": h.smiles,
                "docking_score_kcal_mol": h.docking_score_kcal_mol,
                "cwas_energy": h.cwas_energy,
                "pains_filter_passed": h.pains_filter_passed,
                "rmsd_to_reference": h.rmsd_to_reference,
            }
            for h in hits
        ],
        "clusters": [
            {
                "id": c.id,
                "cluster_label": c.cluster_label,
                "scaffold_smiles": c.scaffold_smiles,
                "member_hits_count": c.member_hits_count,
                "mean_affinity_kcal_mol": c.mean_affinity_kcal_mol,
            }
            for c in clusters
        ],
    }


@router.get("/metrics")
async def get_vhts_metrics(
    db: AsyncSession = Depends(get_db_session),
):
    """Get aggregate statistics for vHTS screening campaigns."""
    repo = VirtualHTSRepository(db)
    return await repo.get_metrics()
