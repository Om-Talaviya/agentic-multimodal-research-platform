"""Phase 130: Precision Oncology Adaptive Chemotherapy Resistance & Clonal Fitness API Routes."""

from typing import Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from database.repositories.adaptive_resistance_repo import AdaptiveResistanceRepository
from research.oncology.adaptive_resistance_engine import (
    AdaptiveResistanceEngine,
    ClonalSpecification,
    DosingRegimenStep,
)

router = APIRouter(prefix="/adaptive-resistance", tags=["Phase 130: Adaptive Resistance Dynamics"])


class CloneInput(BaseModel):
    clone_name: str
    driver_mutations: List[str] = Field(default_factory=list)
    initial_frequency: float = 0.5
    intrinsic_growth_rate: float = 0.04
    ic50: float = 10.0
    phenotype: str = "SENSITIVE"


class DosingStepInput(BaseModel):
    drug_name: str = "Cisplatin"
    dosage: float = 50.0
    duration_days: int = 7
    holiday_days: int = 14


class RunAdaptiveSimulationRequest(BaseModel):
    name: str = Field(..., example="NSCLC Cisplatin Clonal Study")
    cancer_type: str = Field(..., example="Non-Small Cell Lung Cancer")
    patient_id: Optional[str] = Field("PT-1002", example="PT-1002")
    description: Optional[str] = Field(None)
    clones: List[CloneInput] = Field(default_factory=list)
    regimen: List[DosingStepInput] = Field(default_factory=list)
    cycles: int = Field(6, ge=1, le=24)
    adaptive_threshold: float = Field(0.5, ge=0.1, le=1.0)


@router.post("/simulate", status_code=status.HTTP_201_CREATED)
async def simulate_adaptive_resistance(
    req: RunAdaptiveSimulationRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Execute clonal fitness dynamics simulation and persist results."""
    # If no clones provided, default to standard sensitive/resistant pair
    clones_spec = [
        ClonalSpecification(
            clone_name=c.clone_name,
            driver_mutations=c.driver_mutations,
            initial_frequency=c.initial_frequency,
            intrinsic_growth_rate=c.intrinsic_growth_rate,
            ic50=c.ic50,
            phenotype=c.phenotype,
        )
        for c in req.clones
    ] if req.clones else [
        ClonalSpecification(
            clone_name="Clone_WT_Sensitive",
            driver_mutations=["EGFR_L858R"],
            initial_frequency=0.85,
            intrinsic_growth_rate=0.045,
            ic50=5.0,
            phenotype="SENSITIVE",
        ),
        ClonalSpecification(
            clone_name="Clone_T790M_Resistant",
            driver_mutations=["EGFR_L858R", "EGFR_T790M"],
            initial_frequency=0.15,
            intrinsic_growth_rate=0.038,
            ic50=45.0,
            phenotype="MULTI_DRUG_RESISTANT",
        ),
    ]

    regimen_spec = [
        DosingRegimenStep(
            drug_name=r.drug_name,
            dosage=r.dosage,
            duration_days=r.duration_days,
            holiday_days=r.holiday_days,
        )
        for r in req.regimen
    ] if req.regimen else [
        DosingRegimenStep(
            drug_name="Osimertinib",
            dosage=80.0,
            duration_days=7,
            holiday_days=14,
        )
    ]

    engine = AdaptiveResistanceEngine()
    sim_res = engine.simulate_treatment_course(
        study_name=req.name,
        cancer_type=req.cancer_type,
        clones=clones_spec,
        regimen=regimen_spec,
        cycles=req.cycles,
        adaptive_threshold=req.adaptive_threshold,
    )

    repo = AdaptiveResistanceRepository(db)

    study = await repo.create_study(
        name=req.name,
        cancer_type=req.cancer_type,
        patient_id=req.patient_id,
        description=req.description,
        chemo_regimen=[r.model_dump() for r in regimen_spec],
        total_cycles=req.cycles,
        summary_metrics=sim_res.summary_metrics,
    )

    for fc in sim_res.final_clones:
        await repo.add_clonal_lineage(
            study_id=study.id,
            clone_name=fc["clone_name"],
            driver_mutations=fc["driver_mutations"],
            initial_frequency=fc["initial_frequency"],
            final_frequency=fc["final_frequency"],
            intrinsic_fitness=fc["intrinsic_fitness"],
            phenotype=fc["phenotype"],
        )

    for tr in sim_res.trajectories:
        await repo.add_trajectory_point(
            study_id=study.id,
            time_step=tr["time_step"],
            drug_concentration=tr["drug_concentration"],
            tumor_burden=tr["tumor_burden"],
            clone_abundances=tr["clone_abundances"],
            resistance_index=tr["resistance_index"],
            adaptive_recommendation=tr["adaptive_recommendation"],
        )

    return {
        "status": "success",
        "study_id": str(study.id),
        "study_name": study.name,
        "summary_metrics": sim_res.summary_metrics,
        "recommendations": sim_res.recommendations,
        "total_trajectories": len(sim_res.trajectories),
    }


@router.get("/studies", response_model=List[Dict[str, Any]])
async def list_adaptive_studies(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List all adaptive chemotherapy resistance studies."""
    repo = AdaptiveResistanceRepository(db)
    studies = await repo.list_studies(limit=limit, offset=offset)
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "cancer_type": s.cancer_type,
            "patient_id": s.patient_id,
            "total_cycles": s.total_cycles,
            "status": s.status,
            "summary_metrics": s.summary_metrics,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in studies
    ]


@router.get("/studies/{study_id}")
async def get_adaptive_study_details(
    study_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get complete study details including clonal lineages and longitudinal trajectories."""
    repo = AdaptiveResistanceRepository(db)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Adaptive resistance study not found")

    lineages = await repo.get_lineages_by_study(study_id)
    trajectories = await repo.get_trajectories_by_study(study_id)

    return {
        "id": str(study.id),
        "name": study.name,
        "cancer_type": study.cancer_type,
        "patient_id": study.patient_id,
        "description": study.description,
        "chemo_regimen": study.chemo_regimen,
        "total_cycles": study.total_cycles,
        "status": study.status,
        "summary_metrics": study.summary_metrics,
        "created_at": study.created_at.isoformat() if study.created_at else None,
        "clonal_lineages": [
            {
                "id": str(l.id),
                "clone_name": l.clone_name,
                "driver_mutations": l.driver_mutations,
                "initial_frequency": l.initial_frequency,
                "final_frequency": l.final_frequency,
                "intrinsic_fitness": l.intrinsic_fitness,
                "phenotype": l.phenotype,
            }
            for l in lineages
        ],
        "trajectories": [
            {
                "id": str(t.id),
                "time_step": t.time_step,
                "drug_concentration": t.drug_concentration,
                "tumor_burden": t.tumor_burden,
                "clone_abundances": t.clone_abundances,
                "resistance_index": t.resistance_index,
                "adaptive_recommendation": t.adaptive_recommendation,
            }
            for t in trajectories
        ],
    }
