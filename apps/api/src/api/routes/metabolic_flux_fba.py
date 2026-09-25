"""API Router for Genome-Scale Metabolic Network Flux Balance Analysis (FBA)."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.metabolic_flux_fba_repo import MetabolicFluxFBARepository
from research.metabolism.metabolic_flux_fba_engine import MetabolicFluxFBAEngine

router = APIRouter(prefix="/metabolic-flux-fba", tags=["Metabolic Flux FBA"])


class ReactionConstraintInput(BaseModel):
    reaction_id: str = Field("R_HEX1", description="BiGG reaction identifier")
    reaction_name: str = Field("Hexokinase", description="Enzyme reaction description")
    subsystem: str = Field("Glycolysis / Gluconeogenesis", description="Metabolic pathway subsystem")
    lower_bound: float = Field(0.0, description="Flux lower boundary (mmol/gDW/hr)")
    upper_bound: float = Field(1000.0, description="Flux upper boundary (mmol/gDW/hr)")
    computed_flux_mmol_gdw_hr: float = Field(14.85, description="Optimal LP solved flux rate")
    shadow_price: float = Field(-0.12, description="Dual variable shadow price")


class RunFBARequest(BaseModel):
    study_name: str = Field(..., description="Name for the metabolic flux study")
    organism_model: str = Field("Human Recon3D", description="Genome-scale reconstruction model")
    cellular_phenotype: str = Field("Warburg Glycolytic Cancer", description="Cellular state or metabolic condition")
    custom_reactions: Optional[List[ReactionConstraintInput]] = None


@router.post("/simulate", status_code=status.HTTP_201_CREATED)
async def simulate_metabolic_flux(
    payload: RunFBARequest,
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Execute Linear Programming Flux Balance Analysis and target vulnerability evaluation."""
    engine = MetabolicFluxFBAEngine()
    reactions_data = [r.model_dump() for r in payload.custom_reactions] if payload.custom_reactions else None

    result = engine.run_flux_balance_analysis(
        study_name=payload.study_name,
        organism_model=payload.organism_model,
        cellular_phenotype=payload.cellular_phenotype,
        custom_reactions=reactions_data,
    )

    repo = MetabolicFluxFBARepository(session)
    saved_study = await repo.create_study(
        study_name=result["study_name"],
        organism_model=result["organism_model"],
        cellular_phenotype=result["cellular_phenotype"],
        optimal_growth_rate_hr=result["optimal_growth_rate_hr"],
        objective_reaction=result["objective_reaction"],
        summary_metrics=result["summary_metrics"],
        reactions=result["reactions"],
        vulnerabilities=result["vulnerabilities"],
    )

    return {
        "id": str(saved_study.id),
        "status": "success",
        "study_name": saved_study.study_name,
        "organism_model": saved_study.organism_model,
        "cellular_phenotype": saved_study.cellular_phenotype,
        "optimal_growth_rate_hr": saved_study.optimal_growth_rate_hr,
        "objective_reaction": saved_study.objective_reaction,
        "summary_metrics": saved_study.summary_metrics,
        "reactions": [
            {
                "id": str(r.id),
                "reaction_id": r.reaction_id,
                "reaction_name": r.reaction_name,
                "subsystem": r.subsystem,
                "lower_bound": r.lower_bound,
                "upper_bound": r.upper_bound,
                "computed_flux_mmol_gdw_hr": r.computed_flux_mmol_gdw_hr,
                "shadow_price": r.shadow_price,
            }
            for r in saved_study.reactions
        ],
        "vulnerabilities": [
            {
                "id": str(v.id),
                "target_enzyme_gene": v.target_enzyme_gene,
                "target_reaction": v.target_reaction,
                "growth_inhibition_percent": v.growth_inhibition_percent,
                "synthetic_lethal_partner": v.synthetic_lethal_partner,
                "druggability_verdict": v.druggability_verdict,
            }
            for v in saved_study.vulnerabilities
        ],
    }


@router.get("/studies", response_model=List[Dict[str, Any]])
async def list_fba_studies(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """List recent metabolic flux FBA studies."""
    repo = MetabolicFluxFBARepository(session)
    studies = await repo.list_studies(limit=limit, offset=offset)
    return [
        {
            "id": str(s.id),
            "study_name": s.study_name,
            "organism_model": s.organism_model,
            "cellular_phenotype": s.cellular_phenotype,
            "optimal_growth_rate_hr": s.optimal_growth_rate_hr,
            "created_at": s.created_at,
        }
        for s in studies
    ]


@router.get("/studies/{study_id}")
async def get_fba_study(
    study_id: uuid.UUID,
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve details for a specific metabolic flux FBA study."""
    repo = MetabolicFluxFBARepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Metabolic flux study with ID '{study_id}' not found.",
        )

    return {
        "id": str(study.id),
        "study_name": study.study_name,
        "organism_model": study.organism_model,
        "cellular_phenotype": study.cellular_phenotype,
        "optimal_growth_rate_hr": study.optimal_growth_rate_hr,
        "objective_reaction": study.objective_reaction,
        "summary_metrics": study.summary_metrics,
        "reactions": [
            {
                "id": str(r.id),
                "reaction_id": r.reaction_id,
                "reaction_name": r.reaction_name,
                "subsystem": r.subsystem,
                "lower_bound": r.lower_bound,
                "upper_bound": r.upper_bound,
                "computed_flux_mmol_gdw_hr": r.computed_flux_mmol_gdw_hr,
                "shadow_price": r.shadow_price,
            }
            for r in study.reactions
        ],
        "vulnerabilities": [
            {
                "id": str(v.id),
                "target_enzyme_gene": v.target_enzyme_gene,
                "target_reaction": v.target_reaction,
                "growth_inhibition_percent": v.growth_inhibition_percent,
                "synthetic_lethal_partner": v.synthetic_lethal_partner,
                "druggability_verdict": v.druggability_verdict,
            }
            for v in study.vulnerabilities
        ],
        "created_at": study.created_at,
    }


@router.delete("/studies/{study_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fba_study(
    study_id: uuid.UUID,
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    """Delete a metabolic flux study record by ID."""
    repo = MetabolicFluxFBARepository(session)
    deleted = await repo.delete_study(study_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Metabolic flux study with ID '{study_id}' not found.",
        )
