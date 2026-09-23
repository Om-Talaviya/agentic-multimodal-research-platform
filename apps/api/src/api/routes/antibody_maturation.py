"""
Phase 127: Autonomous In-Silico Antibody Affinity Maturation API Routes.
"""
from typing import Dict, Any, Optional, List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from database.repositories.antibody_maturation_repo import AntibodyMaturationRepository
from research.immunology.antibody_maturation_engine import AntibodyAffinityMaturationEngine

router = APIRouter(prefix="/antibody-maturation", tags=["Phase 127: Antibody Affinity Maturation"])


class MatureAntibodyRequest(BaseModel):
    candidate_name: str = Field(..., example="mAb-HER2-Trastuzumab-Evol")
    target_antigen: str = Field("HER2 Extracellular Domain IV", example="HER2 Extracellular Domain IV")
    parental_kd_nm: float = Field(12.5, ge=0.01)
    evolution_rounds: int = Field(4, ge=1, le=10)
    project_id: Optional[str] = Field(None)


@router.post("/mature", status_code=status.HTTP_201_CREATED)
async def mature_antibody_lead(
    req: MatureAntibodyRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Executes in-silico somatic hypermutation affinity maturation campaign.
    """
    engine = AntibodyAffinityMaturationEngine()
    sim_res = engine.simulate_maturation_campaign(
        candidate_name=req.candidate_name,
        target_antigen=req.target_antigen,
        parental_kd_nm=req.parental_kd_nm,
        evolution_rounds=req.evolution_rounds,
    )

    repo = AntibodyMaturationRepository(db)
    campaign = await repo.create_campaign(
        candidate_name=req.candidate_name,
        target_antigen=req.target_antigen,
        parental_kd_nm=req.parental_kd_nm,
        matured_kd_nm=sim_res["matured_kd_nm"],
        affinity_fold_improvement=sim_res["affinity_fold_improvement"],
        humanness_score_oasis=sim_res["humanness_score_oasis"],
        thermostability_tm_celsius=sim_res["thermostability_tm_celsius"],
        evolution_rounds=req.evolution_rounds,
        metadata_json={"summary": sim_res["summary"]},
        project_id=req.project_id,
    )

    # Persist variants
    for v in sim_res["top_variants"]:
        await repo.add_variant(
            campaign_id=campaign.id,
            variant_id=v["variant_id"],
            cdr_region=v["cdr_region"],
            mutations_summary=v["mutations"],
            predicted_binding_energy_ddg=v["predicted_ddg_kcal_mol"],
            dissociation_constant_kd_nm=v["predicted_kd_nm"],
            developability_flag=v["developability_pass"],
            polyreactivity_risk=v["polyreactivity_risk"],
        )

    # Persist contacts
    for c in sim_res["key_contacts"]:
        await repo.add_contact(
            campaign_id=campaign.id,
            antibody_residue=c["antibody_residue"],
            antigen_residue=c["antigen_residue"],
            interaction_type=c["interaction_type"],
            interaction_distance_angstrom=c["distance_angstrom"],
            binding_energy_contribution_kcal=c["energy_kcal"],
        )

    saved = await repo.get_campaign(campaign.id)
    return {
        "status": "success",
        "campaign_id": str(campaign.id),
        "candidate_name": campaign.candidate_name,
        "matured_kd_nm": campaign.matured_kd_nm,
        "affinity_fold_improvement": campaign.affinity_fold_improvement,
        "variants_count": len(saved.variants) if saved else 0,
        "contacts_count": len(saved.contacts) if saved else 0,
        "summary": sim_res["summary"],
    }


@router.get("/campaigns", status_code=status.HTTP_200_OK)
async def list_maturation_campaigns(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """List antibody affinity maturation campaigns."""
    repo = AntibodyMaturationRepository(db)
    campaigns = await repo.list_campaigns(limit=limit)
    return [
        {
            "id": str(c.id),
            "candidate_name": c.candidate_name,
            "target_antigen": c.target_antigen,
            "parental_kd_nm": c.parental_kd_nm,
            "matured_kd_nm": c.matured_kd_nm,
            "fold_improvement": c.affinity_fold_improvement,
            "humanness_score": c.humanness_score_oasis,
            "variants_count": len(c.variants),
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in campaigns
    ]


@router.get("/campaigns/{campaign_id}", status_code=status.HTTP_200_OK)
async def get_maturation_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get single antibody affinity maturation campaign details."""
    repo = AntibodyMaturationRepository(db)
    campaign = await repo.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found",
        )
    return {
        "id": str(campaign.id),
        "candidate_name": campaign.candidate_name,
        "target_antigen": campaign.target_antigen,
        "parental_kd_nm": campaign.parental_kd_nm,
        "matured_kd_nm": campaign.matured_kd_nm,
        "affinity_fold_improvement": campaign.affinity_fold_improvement,
        "humanness_score_oasis": campaign.humanness_score_oasis,
        "thermostability_tm_celsius": campaign.thermostability_tm_celsius,
        "variants": [
            {
                "variant_id": v.variant_id,
                "cdr_region": v.cdr_region,
                "mutations": v.mutations_summary,
                "ddg": v.predicted_binding_energy_ddg,
                "kd_nm": v.dissociation_constant_kd_nm,
                "developability": v.developability_flag,
            }
            for v in campaign.variants
        ],
        "contacts": [
            {
                "antibody_residue": c.antibody_residue,
                "antigen_residue": c.antigen_residue,
                "interaction_type": c.interaction_type,
                "distance": c.interaction_distance_angstrom,
                "energy_kcal": c.binding_energy_contribution_kcal,
            }
            for c in campaign.contacts
        ],
    }
