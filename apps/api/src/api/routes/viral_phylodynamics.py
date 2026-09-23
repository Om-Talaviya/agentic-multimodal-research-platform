"""
Phase 132: Global Pandemic Biosurveillance & Multi-Strain Viral Lineage Phylodynamics API Routes.
"""

from typing import Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from database.repositories.viral_phylodynamics_repo import ViralPhylodynamicsRepository
from research.epidemiology.viral_phylodynamics_engine import (
    ViralPhylodynamicsEngine,
    LineageSeed,
)

router = APIRouter(prefix="/viral-phylodynamics", tags=["Phase 132: Viral Phylodynamics & Biosurveillance"])


class LineageSeedInput(BaseModel):
    clade_name: str
    pangolin_designation: str
    who_label: Optional[str] = None
    defining_mutations: List[str] = Field(default_factory=list)
    initial_proportion: float = 0.5
    fitness_advantage: float = 0.08


class RunSurveillanceSimulationRequest(BaseModel):
    pathogen_name: str = Field(..., example="SARS-CoV-2")
    genome_type: str = Field("ssRNA(+)", example="ssRNA(+)")
    geographic_regions: List[str] = Field(default_factory=lambda: ["Global", "North America", "Europe", "Asia"])
    total_days: int = Field(90, ge=15, le=365)
    baseline_r0: float = Field(2.8, ge=0.5, le=10.0)
    lineages: List[LineageSeedInput] = Field(default_factory=list)
    project_id: Optional[str] = Field(None)


@router.post("/simulate", status_code=status.HTTP_201_CREATED)
async def simulate_viral_phylodynamics(
    req: RunSurveillanceSimulationRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Execute phylodynamic renewal process and persist biosurveillance study."""
    seeds_spec = [
        LineageSeed(
            clade_name=l.clade_name,
            pangolin_designation=l.pangolin_designation,
            who_label=l.who_label,
            defining_mutations=l.defining_mutations,
            initial_proportion=l.initial_proportion,
            fitness_advantage=l.fitness_advantage,
        )
        for l in req.lineages
    ] if req.lineages else None

    engine = ViralPhylodynamicsEngine()
    sim_res = engine.simulate_phylodynamics(
        pathogen_name=req.pathogen_name,
        seeds=seeds_spec,
        total_days=req.total_days,
        baseline_r0=req.baseline_r0,
    )

    repo = ViralPhylodynamicsRepository(db)
    study = await repo.create_study(
        pathogen_name=req.pathogen_name,
        genome_type=req.genome_type,
        geographic_regions=req.geographic_regions,
        total_genomes_sequenced=sim_res.total_genomes_analyzed,
        effective_reproduction_number_rt=sim_res.effective_reproduction_number_rt,
        transmission_fitness_gain_pct=sim_res.transmission_fitness_gain_pct,
        metadata_json={
            "summary_metrics": sim_res.summary_metrics,
            "trajectories": sim_res.epidemiological_trajectories,
            "tree_nodes": sim_res.phylogenetic_tree_nodes,
        },
        project_id=req.project_id,
    )

    for lin in sim_res.lineages:
        await repo.add_lineage(
            study_id=study.id,
            lineage_clade=lin["lineage_clade"],
            pangolin_designation=lin["pangolin_designation"],
            who_label=lin.get("who_label"),
            defining_mutations=lin["defining_mutations"],
            growth_advantage_daily=lin["growth_advantage_daily"],
            immune_evasion_score=lin["immune_evasion_score"],
            global_prevalence_pct=lin["global_prevalence_pct"],
        )

        await repo.add_fitness_profile(
            study_id=study.id,
            clade_name=lin["lineage_clade"],
            basic_reproduction_number_r0=req.baseline_r0 * (1.0 + lin["growth_advantage_daily"] * 5.0),
            serial_interval_days=3.6,
            ace2_binding_affinity_shift=round(1.0 + lin["growth_advantage_daily"] * 10.0, 2),
            cross_neutralization_titer_fold_drop=round(lin["immune_evasion_score"] * 15.0, 1),
        )

    return {
        "status": "success",
        "study_id": str(study.id),
        "pathogen_name": study.pathogen_name,
        "effective_reproduction_number_rt": sim_res.effective_reproduction_number_rt,
        "transmission_fitness_gain_pct": sim_res.transmission_fitness_gain_pct,
        "lineages_count": len(sim_res.lineages),
        "summary_metrics": sim_res.summary_metrics,
        "recommendations": sim_res.recommendations,
    }


@router.get("/studies", response_model=List[Dict[str, Any]])
async def list_surveillance_studies(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List all global viral surveillance studies."""
    repo = ViralPhylodynamicsRepository(db)
    studies = await repo.list_studies(limit=limit, offset=offset)
    return [
        {
            "id": str(s.id),
            "pathogen_name": s.pathogen_name,
            "genome_type": s.genome_type,
            "geographic_regions": s.geographic_regions,
            "total_genomes_sequenced": s.total_genomes_sequenced,
            "effective_reproduction_number_rt": s.effective_reproduction_number_rt,
            "transmission_fitness_gain_pct": s.transmission_fitness_gain_pct,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in studies
    ]


@router.get("/studies/{study_id}")
async def get_surveillance_study_details(
    study_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get complete study details including tracked clades and transmission fitness."""
    repo = ViralPhylodynamicsRepository(db)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Viral surveillance study not found")

    return {
        "id": str(study.id),
        "pathogen_name": study.pathogen_name,
        "genome_type": study.genome_type,
        "geographic_regions": study.geographic_regions,
        "total_genomes_sequenced": study.total_genomes_sequenced,
        "effective_reproduction_number_rt": study.effective_reproduction_number_rt,
        "transmission_fitness_gain_pct": study.transmission_fitness_gain_pct,
        "metadata_json": study.metadata_json,
        "created_at": study.created_at.isoformat() if study.created_at else None,
        "lineages": [
            {
                "id": str(l.id),
                "lineage_clade": l.lineage_clade,
                "pangolin_designation": l.pangolin_designation,
                "who_label": l.who_label,
                "defining_mutations": l.defining_mutations,
                "growth_advantage_daily": l.growth_advantage_daily,
                "immune_evasion_score": l.immune_evasion_score,
                "global_prevalence_pct": l.global_prevalence_pct,
            }
            for l in study.lineages
        ],
        "fitness_profiles": [
            {
                "id": str(f.id),
                "clade_name": f.clade_name,
                "basic_reproduction_number_r0": f.basic_reproduction_number_r0,
                "serial_interval_days": f.serial_interval_days,
                "ace2_binding_affinity_shift": f.ace2_binding_affinity_shift,
                "cross_neutralization_titer_fold_drop": f.cross_neutralization_titer_fold_drop,
            }
            for f in study.fitness_profiles
        ],
    }
