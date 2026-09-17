"""REST API endpoints for Clinical Trial Site Selection & Protocol Feasibility."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.models import User
from database.repositories.clinical_site_selection_repo import ClinicalSiteSelectionRepository
from research.clinical.site_selection_engine import ClinicalSiteSelectionEngine

router = APIRouter(prefix="/api/v1/clinical-sites", tags=["Clinical Trial Site Selection & Feasibility"])
engine = ClinicalSiteSelectionEngine()


class SiteInput(BaseModel):
    site_name: str
    country: str
    city: str
    principal_investigator: str
    historical_recruitment_rate: float = Field(1.0, ge=0.0)
    ethics_approval_timeline_days: int = Field(45, ge=1)
    patient_pool_density: int = Field(1000, ge=1)
    pi_experience_years: float = Field(5.0, ge=0.0)
    competing_trials_count: int = Field(1, ge=0)


class StudyEvaluationRequest(BaseModel):
    study_title: str
    protocol_code: str
    indication: str
    phase: str = "Phase 2"
    target_enrollment: int = Field(100, ge=1)
    recruitment_duration_months: float = Field(12.0, ge=1.0)
    dropout_rate: float = Field(0.10, ge=0.0, le=0.50)
    sites: List[SiteInput]


class SimulationRequest(BaseModel):
    simulation_name: str = "Recruitment Monte Carlo Run"
    dropout_rate: float = Field(0.10, ge=0.0, le=0.50)
    n_simulations: int = Field(100, ge=10, le=1000)


@router.post("/studies/evaluate", status_code=status.HTTP_201_CREATED)
async def evaluate_and_create_study(
    req: StudyEvaluationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Evaluates protocol feasibility, scores candidate sites, runs stochastic simulation, and stores records."""
    repo = ClinicalSiteSelectionRepository(db)

    # Convert sites to dicts
    sites_dict = [s.model_dump() for s in req.sites]
    eval_res = engine.evaluate_study_feasibility(
        study_data={
            "study_title": req.study_title,
            "protocol_code": req.protocol_code,
            "indication": req.indication,
            "phase": req.phase,
            "target_enrollment": req.target_enrollment,
            "recruitment_duration_months": req.recruitment_duration_months,
        },
        sites_input=sites_dict,
        dropout_rate=req.dropout_rate,
    )

    study = await repo.create_study(
        study_title=req.study_title,
        protocol_code=req.protocol_code,
        indication=req.indication,
        phase=req.phase,
        target_enrollment=req.target_enrollment,
        recruitment_duration_months=req.recruitment_duration_months,
        total_sites=len(eval_res["evaluated_sites"]),
    )

    created_sites = await repo.add_sites(study.id, eval_res["evaluated_sites"])

    sim_data = eval_res["simulation"]
    created_sim = await repo.add_simulation(
        study_id=study.id,
        simulation_name=sim_data["simulation_name"],
        target_timeline_months=sim_data["target_timeline_months"],
        p10_completion_months=sim_data["p10_completion_months"],
        p50_completion_months=sim_data["p50_completion_months"],
        p90_completion_months=sim_data["p90_completion_months"],
        dropout_rate=sim_data["dropout_rate"],
        enrollment_curve_json=sim_data["enrollment_curve_json"],
        bottleneck_risks_json=sim_data["bottleneck_risks_json"],
    )

    return {
        "id": study.id,
        "study_title": study.study_title,
        "protocol_code": study.protocol_code,
        "indication": study.indication,
        "phase": study.phase,
        "target_enrollment": study.target_enrollment,
        "recruitment_duration_months": study.recruitment_duration_months,
        "total_sites": study.total_sites,
        "sites": [
            {
                "id": s.id,
                "site_name": s.site_name,
                "country": s.country,
                "city": s.city,
                "principal_investigator": s.principal_investigator,
                "feasibility_score": s.feasibility_score,
                "risk_tier": s.risk_tier,
                "selected_for_trial": s.selected_for_trial,
                "metrics": s.metrics_json,
            }
            for s in created_sites
        ],
        "simulation": {
            "id": created_sim.id,
            "simulation_name": created_sim.simulation_name,
            "p10_completion_months": created_sim.p10_completion_months,
            "p50_completion_months": created_sim.p50_completion_months,
            "p90_completion_months": created_sim.p90_completion_months,
            "enrollment_curve": created_sim.enrollment_curve_json,
            "bottleneck_risks": created_sim.bottleneck_risks_json,
        }
    }


@router.get("/studies")
async def list_studies(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists clinical site selection studies."""
    repo = ClinicalSiteSelectionRepository(db)
    studies = await repo.list_studies(limit=limit, offset=offset)
    return [
        {
            "id": s.id,
            "study_title": s.study_title,
            "protocol_code": s.protocol_code,
            "indication": s.indication,
            "phase": s.phase,
            "target_enrollment": s.target_enrollment,
            "recruitment_duration_months": s.recruitment_duration_months,
            "total_sites": s.total_sites,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in studies
    ]


@router.get("/studies/{study_id}")
async def get_study_details(
    study_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Gets detailed study records including sites and recruitment simulations."""
    repo = ClinicalSiteSelectionRepository(db)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    sites = await repo.get_sites_by_study(study_id)
    simulations = await repo.get_simulations_by_study(study_id)

    return {
        "id": study.id,
        "study_title": study.study_title,
        "protocol_code": study.protocol_code,
        "indication": study.indication,
        "phase": study.phase,
        "target_enrollment": study.target_enrollment,
        "recruitment_duration_months": study.recruitment_duration_months,
        "total_sites": study.total_sites,
        "sites": [
            {
                "id": s.id,
                "site_name": s.site_name,
                "country": s.country,
                "city": s.city,
                "principal_investigator": s.principal_investigator,
                "feasibility_score": s.feasibility_score,
                "risk_tier": s.risk_tier,
                "selected_for_trial": s.selected_for_trial,
                "metrics": s.metrics_json,
            }
            for s in sites
        ],
        "simulations": [
            {
                "id": sim.id,
                "simulation_name": sim.simulation_name,
                "p10_completion_months": sim.p10_completion_months,
                "p50_completion_months": sim.p50_completion_months,
                "p90_completion_months": sim.p90_completion_months,
                "dropout_rate": sim.dropout_rate,
                "enrollment_curve": sim.enrollment_curve_json,
                "bottleneck_risks": sim.bottleneck_risks_json,
            }
            for sim in simulations
        ]
    }


@router.post("/studies/{study_id}/simulate")
async def run_simulation(
    study_id: str,
    req: SimulationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Runs a new Monte Carlo recruitment simulation for an existing study."""
    repo = ClinicalSiteSelectionRepository(db)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    sites = await repo.get_sites_by_study(study_id)
    sites_dict = [
        {
            "site_name": s.site_name,
            "country": s.country,
            "historical_recruitment_rate": s.historical_recruitment_rate,
            "ethics_approval_timeline_days": s.ethics_approval_timeline_days,
            "selected_for_trial": s.selected_for_trial,
        }
        for s in sites
    ]

    sim_res = engine.simulate_recruitment(
        target_enrollment=study.target_enrollment,
        recruitment_duration_months=study.recruitment_duration_months,
        sites=sites_dict,
        dropout_rate=req.dropout_rate,
        n_simulations=req.n_simulations,
    )

    created_sim = await repo.add_simulation(
        study_id=study.id,
        simulation_name=req.simulation_name,
        target_timeline_months=sim_res["target_timeline_months"],
        p10_completion_months=sim_res["p10_completion_months"],
        p50_completion_months=sim_res["p50_completion_months"],
        p90_completion_months=sim_res["p90_completion_months"],
        dropout_rate=sim_res["dropout_rate"],
        enrollment_curve_json=sim_res["enrollment_curve_json"],
        bottleneck_risks_json=sim_res["bottleneck_risks_json"],
    )

    return {
        "id": created_sim.id,
        "simulation_name": created_sim.simulation_name,
        "p10_completion_months": created_sim.p10_completion_months,
        "p50_completion_months": created_sim.p50_completion_months,
        "p90_completion_months": created_sim.p90_completion_months,
        "dropout_rate": created_sim.dropout_rate,
        "enrollment_curve": created_sim.enrollment_curve_json,
        "bottleneck_risks": created_sim.bottleneck_risks_json,
    }
