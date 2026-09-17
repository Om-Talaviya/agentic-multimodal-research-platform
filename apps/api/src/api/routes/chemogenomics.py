"""REST API endpoints for Chemogenomics Polypharmacology & Off-Target Interactome."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.models import User
from database.repositories.chemogenomics_repo import ChemogenomicsRepository
from research.chemogenomics.polypharmacology_engine import ChemogenomicsPolypharmacologyEngine

router = APIRouter(prefix="/api/v1/chemogenomics", tags=["Chemogenomics Polypharmacology & Kinome Interactome"])
engine = ChemogenomicsPolypharmacologyEngine()


class TargetAffinityInput(BaseModel):
    target_gene: str
    uniprot_id: str
    protein_family: str = "KINASE"
    affinity_type: str = "IC50"
    affinity_value_nm: float = Field(..., ge=0.01)
    is_primary_target: bool = False


class CompoundScreenRequest(BaseModel):
    compound_name: str
    smiles: str
    primary_target: str = "ABL1"
    affinities: Optional[List[TargetAffinityInput]] = None


@router.post("/profiles/screen", status_code=status.HTTP_201_CREATED)
async def screen_compound_polypharmacology(
    req: CompoundScreenRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Screens small molecule polypharmacology, calculates Gini selectivity index, and flags antitarget alerts."""
    repo = ChemogenomicsRepository(db)

    affinities_dict = [a.model_dump() for a in req.affinities] if req.affinities else None
    eval_res = engine.screen_compound(req.model_dump(), affinities_dict)

    profile = await repo.create_profile(
        compound_name=eval_res["compound_name"],
        smiles=eval_res["smiles"],
        primary_target=eval_res["primary_target"],
        gini_selectivity_index=eval_res["gini_selectivity_index"],
        selectivity_tier=eval_res["selectivity_tier"],
        total_targets_screened=eval_res["total_targets_screened"],
        off_target_liabilities_count=eval_res["off_target_liabilities_count"],
        profile_summary_json=eval_res["profile_summary_json"],
    )

    created_affinities = await repo.add_affinities(profile.id, eval_res["affinities"])
    created_alerts = await repo.add_alerts(profile.id, eval_res["alerts"])

    return {
        "id": profile.id,
        "compound_name": profile.compound_name,
        "primary_target": profile.primary_target,
        "gini_selectivity_index": profile.gini_selectivity_index,
        "selectivity_tier": profile.selectivity_tier,
        "total_targets_screened": profile.total_targets_screened,
        "off_target_liabilities_count": profile.off_target_liabilities_count,
        "summary": profile.profile_summary_json,
        "affinities": [
            {
                "target_gene": a.target_gene,
                "uniprot_id": a.uniprot_id,
                "protein_family": a.protein_family,
                "affinity_type": a.affinity_type,
                "affinity_value_nm": a.affinity_value_nm,
                "is_primary_target": a.is_primary_target,
                "is_off_target_liability": a.is_off_target_liability,
            }
            for a in created_affinities
        ],
        "alerts": [
            {
                "target_gene": al.target_gene,
                "risk_type": al.risk_type,
                "binding_potency_nm": al.binding_potency_nm,
                "severity": al.severity,
                "recommendation": al.recommendation,
            }
            for al in created_alerts
        ]
    }


@router.get("/profiles")
async def list_profiles(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists chemogenomics polypharmacology profiles."""
    repo = ChemogenomicsRepository(db)
    profiles = await repo.list_profiles(limit=limit, offset=offset)
    return [
        {
            "id": p.id,
            "compound_name": p.compound_name,
            "primary_target": p.primary_target,
            "gini_selectivity_index": p.gini_selectivity_index,
            "selectivity_tier": p.selectivity_tier,
            "off_target_liabilities_count": p.off_target_liabilities_count,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in profiles
    ]


@router.get("/profiles/{profile_id}")
async def get_profile_details(
    profile_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Gets detailed compound polypharmacology profile with target affinities and safety alerts."""
    repo = ChemogenomicsRepository(db)
    profile = await repo.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Chemogenomics profile not found")

    affinities = await repo.get_affinities_by_profile(profile_id)
    alerts = await repo.get_alerts_by_profile(profile_id)

    return {
        "id": profile.id,
        "compound_name": profile.compound_name,
        "smiles": profile.smiles,
        "primary_target": profile.primary_target,
        "gini_selectivity_index": profile.gini_selectivity_index,
        "selectivity_tier": profile.selectivity_tier,
        "total_targets_screened": profile.total_targets_screened,
        "off_target_liabilities_count": profile.off_target_liabilities_count,
        "summary": profile.profile_summary_json,
        "affinities": [
            {
                "id": a.id,
                "target_gene": a.target_gene,
                "uniprot_id": a.uniprot_id,
                "protein_family": a.protein_family,
                "affinity_type": a.affinity_type,
                "affinity_value_nm": a.affinity_value_nm,
                "is_primary_target": a.is_primary_target,
                "is_off_target_liability": a.is_off_target_liability,
            }
            for a in affinities
        ],
        "alerts": [
            {
                "id": al.id,
                "target_gene": al.target_gene,
                "risk_type": al.risk_type,
                "binding_potency_nm": al.binding_potency_nm,
                "severity": al.severity,
                "recommendation": al.recommendation,
            }
            for al in alerts
        ]
    }
