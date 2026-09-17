from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.synthetic_lethality_repo import SyntheticLethalityRepository
from research.lethality.lethality_engine import SyntheticLethalityEngine

router = APIRouter(prefix="/api/v1/synthetic-lethality", tags=["Synthetic Lethality & Target Validation"])

class SyntheticLethalScreenRequest(BaseModel):
    screen_name: str = Field(..., example="BRCA1 Deficient Paralog & DNA Repair Screen")
    primary_target_gene: str = Field(..., example="BRCA1")
    tumor_indication: str = Field("Ovarian Carcinoma", example="Ovarian Carcinoma")
    ceres_dependency_threshold: float = Field(-0.5, example=-0.5)
    sample_cell_lines_count: int = Field(8, example=8)

@router.post("/screen", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def screen_synthetic_lethality(
    request: SyntheticLethalScreenRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Autonomous Target Validation & CRISPR Synthetic Lethality Matrix Engine.
    """
    engine = SyntheticLethalityEngine()
    repo = SyntheticLethalityRepository(db)

    # 1. Discover partners
    partners = engine.discover_synthetic_lethal_partners(
        target_gene=request.primary_target_gene,
        tumor_indication=request.tumor_indication,
        ceres_threshold=request.ceres_dependency_threshold,
    )

    # 2. Simulate CRISPR co-dependencies
    top_partner = partners[0]["partner_gene"] if partners else "PARP1"
    dep_profiles = engine.simulate_crispr_dependency_profiles(
        primary_gene=request.primary_target_gene,
        partner_gene=top_partner,
        sample_cell_lines_count=request.sample_cell_lines_count,
    )

    # 3. Create screen DB record
    screen = await repo.create_screen(
        screen_name=request.screen_name,
        primary_target_gene=request.primary_target_gene,
        tumor_indication=request.tumor_indication,
        ceres_dependency_threshold=request.ceres_dependency_threshold,
        sample_cell_lines_count=len(dep_profiles),
    )

    # 4. Persist partners
    for p in partners:
        await repo.add_synthetic_lethal_partner(
            screen_id=screen.id,
            partner_gene=p["partner_gene"],
            interaction_type=p["interaction_type"],
            ceres_depmap_delta_score=p["ceres_depmap_delta_score"],
            synthetic_lethal_p_value=p["synthetic_lethal_p_value"],
            is_validated_druggable=p["is_validated_druggable"],
            confidence_tier=p["confidence_tier"],
        )

    # 5. Persist dependency scores
    for d in dep_profiles:
        await repo.add_dependency_score(
            screen_id=screen.id,
            cell_line_name=d["cell_line_name"],
            lineage=d["lineage"],
            primary_gene_dependency_score=d["primary_gene_dependency_score"],
            partner_gene_dependency_score=d["partner_gene_dependency_score"],
            co_essentiality_correlation=d["co_essentiality_correlation"],
        )

    hydrated = await repo.get_screen_by_id(screen.id)

    return {
        "status": "SUCCESS",
        "screen_id": hydrated.id,
        "screen_name": hydrated.screen_name,
        "primary_target_gene": hydrated.primary_target_gene,
        "tumor_indication": hydrated.tumor_indication,
        "partners_count": len(hydrated.partners),
        "partners": [
            {
                "partner_gene": p.partner_gene,
                "interaction_type": p.interaction_type,
                "ceres_depmap_delta_score": p.ceres_depmap_delta_score,
                "synthetic_lethal_p_value": p.synthetic_lethal_p_value,
                "confidence_tier": p.confidence_tier,
                "is_validated_druggable": p.is_validated_druggable,
            }
            for p in hydrated.partners
        ],
        "dependency_profiles": [
            {
                "cell_line_name": d.cell_line_name,
                "lineage": d.lineage,
                "primary_gene_dependency_score": d.primary_gene_dependency_score,
                "partner_gene_dependency_score": d.partner_gene_dependency_score,
                "co_essentiality_correlation": d.co_essentiality_correlation,
            }
            for d in hydrated.dependency_scores
        ],
    }

@router.get("/screens", response_model=List[Dict[str, Any]])
async def list_synthetic_lethal_screens(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    repo = SyntheticLethalityRepository(db)
    screens = await repo.list_screens(limit=limit)
    return [
        {
            "id": s.id,
            "screen_name": s.screen_name,
            "primary_target_gene": s.primary_target_gene,
            "tumor_indication": s.tumor_indication,
            "partners_count": len(s.partners),
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in screens
    ]

@router.get("/screens/{screen_id}", response_model=Dict[str, Any])
async def get_synthetic_lethal_screen(
    screen_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    repo = SyntheticLethalityRepository(db)
    s = await repo.get_screen_by_id(screen_id)
    if not s:
        raise HTTPException(status_code=404, detail="Synthetic lethal screen not found")
    return {
        "id": s.id,
        "screen_name": s.screen_name,
        "primary_target_gene": s.primary_target_gene,
        "tumor_indication": s.tumor_indication,
        "ceres_dependency_threshold": s.ceres_dependency_threshold,
        "sample_cell_lines_count": s.sample_cell_lines_count,
        "partners": [
            {
                "id": p.id,
                "partner_gene": p.partner_gene,
                "interaction_type": p.interaction_type,
                "ceres_depmap_delta_score": p.ceres_depmap_delta_score,
                "synthetic_lethal_p_value": p.synthetic_lethal_p_value,
                "confidence_tier": p.confidence_tier,
                "is_validated_druggable": p.is_validated_druggable,
            }
            for p in s.partners
        ],
        "dependency_scores": [
            {
                "id": d.id,
                "cell_line_name": d.cell_line_name,
                "lineage": d.lineage,
                "primary_gene_dependency_score": d.primary_gene_dependency_score,
                "partner_gene_dependency_score": d.partner_gene_dependency_score,
                "co_essentiality_correlation": d.co_essentiality_correlation,
            }
            for d in s.dependency_scores
        ],
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }
