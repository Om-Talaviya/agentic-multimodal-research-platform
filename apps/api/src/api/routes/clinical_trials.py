"""
FastAPI Route Handlers for Phase 46: Clinical Trial Protocol Optimization & Cohort Stratification.
"""
import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session, get_current_user
from database.models.user import User as DBUser
from database.repositories.clinical_trial_repo import ClinicalTrialRepository
from research.clinical_trial_engine import ClinicalTrialOptimizerEngine

router = APIRouter(prefix="/clinical-trials", tags=["Clinical Trial Optimizer (Phase 46)"])

class ProtocolOptimizeRequest(BaseModel):
    title: str = Field(..., example="Phase II Study of Multi-Target Kinase Inhibitor AGY-801 in Refractory NSCLC")
    indication: str = Field(..., example="Non-Small Cell Lung Cancer (NSCLC)")
    investigational_agent: str = Field(..., example="AGY-801")
    phase: str = Field(default="Phase II", example="Phase II")
    target_power: float = Field(default=0.85, example=0.85)

class ProtocolResponse(BaseModel):
    id: uuid.UUID
    title: str
    phase: str
    target_indication: str
    investigational_agent: str
    primary_endpoint: str
    sample_size_target: int
    statistical_power: float
    estimated_duration_months: int
    status: str
    protocol_summary: Optional[str] = None
    created_at: Any

    class Config:
        from_attributes = True

@router.post("/optimize", response_model=ProtocolResponse, status_code=status.HTTP_201_CREATED)
async def optimize_and_create_protocol(
    payload: ProtocolOptimizeRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: DBUser = Depends(get_current_user)
):
    engine = ClinicalTrialOptimizerEngine()
    result = engine.optimize_protocol(
        title=payload.title,
        indication=payload.indication,
        agent=payload.investigational_agent,
        phase=payload.phase,
        target_power=payload.target_power
    )

    repo = ClinicalTrialRepository(db)
    protocol = await repo.create_protocol(
        title=result["title"],
        phase=result["phase"],
        target_indication=result["target_indication"],
        investigational_agent=result["investigational_agent"],
        primary_endpoint=result["primary_endpoint"],
        sample_size_target=result["sample_size_target"],
        statistical_power=result["statistical_power"],
        estimated_duration_months=result["estimated_duration_months"],
        protocol_summary=result["protocol_summary"],
        user_id=current_user.id
    )

    for crit in result["criteria"]:
        await repo.add_criteria(
            protocol_id=protocol.id,
            criterion_type=crit["criterion_type"],
            description=crit["description"],
            category=crit["category"],
            structured_rule=crit["structured_rule"],
            impact_on_enrollment_rate=crit["impact_on_enrollment_rate"]
        )

    await repo.add_cohort_matches(protocol_id=protocol.id, matches=result["patients"])

    syn = result["synthetic_arm"]
    await repo.create_synthetic_control_arm(
        protocol_id=protocol.id,
        rwe_data_source=syn["rwe_data_source"],
        baseline_patient_count=syn["baseline_patient_count"],
        matched_patient_count=syn["matched_patient_count"],
        median_os_control=syn["median_os_control"],
        median_os_interventional=syn["median_os_interventional"],
        p_value=syn["p_value"],
        hazard_ratio=syn["hazard_ratio"],
        survival_curve=syn["survival_curve"]
    )

    return protocol

@router.get("/protocols", response_model=List[ProtocolResponse])
async def list_protocols(
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session),
    current_user: DBUser = Depends(get_current_user)
):
    repo = ClinicalTrialRepository(db)
    return await repo.list_protocols(limit=limit)

@router.get("/protocols/{protocol_id}")
async def get_protocol_details(
    protocol_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: DBUser = Depends(get_current_user)
):
    repo = ClinicalTrialRepository(db)
    protocol = await repo.get_protocol(protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    return {
        "id": str(protocol.id),
        "title": protocol.title,
        "phase": protocol.phase,
        "target_indication": protocol.target_indication,
        "investigational_agent": protocol.investigational_agent,
        "primary_endpoint": protocol.primary_endpoint,
        "sample_size_target": protocol.sample_size_target,
        "statistical_power": protocol.statistical_power,
        "estimated_duration_months": protocol.estimated_duration_months,
        "status": protocol.status,
        "protocol_summary": protocol.protocol_summary,
        "criteria": [
            {
                "id": str(c.id),
                "type": c.criterion_type,
                "category": c.category,
                "description": c.description,
                "impact": c.impact_on_enrollment_rate
            } for c in protocol.eligibility_criteria
        ],
        "cohort_matches": [
            {
                "patient_identifier": p.patient_identifier,
                "match_score": p.phenotype_match_score,
                "verdict": p.eligibility_verdict,
                "survival_estimate_months": p.survival_estimate_months,
                "hazard_ratio": p.hazard_ratio
            } for p in protocol.cohort_matches
        ],
        "synthetic_arms": [
            {
                "rwe_source": s.rwe_data_source,
                "matched_count": s.matched_patient_count,
                "median_os_control": s.median_overall_survival_control_months,
                "median_os_interventional": s.median_overall_survival_interventional_months,
                "hazard_ratio": s.hazard_ratio,
                "p_value": s.p_value_log_rank,
                "curve": s.survival_curve_data
            } for s in protocol.synthetic_arms
        ]
    }
