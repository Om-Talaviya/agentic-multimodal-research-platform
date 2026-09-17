"""REST API endpoints for Pharmacovigilance Real-World Safety Signal Mining."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.models import User
from database.repositories.pv_signal_mining_repo import PVSignalMiningRepository
from research.pharmacovigilance.signal_mining_engine import PVSignalMiningEngine

router = APIRouter(prefix="/api/v1/pv-sentinel", tags=["Pharmacovigilance Real-World Safety Sentinel"])
engine = PVSignalMiningEngine()


class StudyMiningRequest(BaseModel):
    study_name: str
    drug_name: str
    active_substance: str
    target_adverse_event: str
    data_source: str = "FAERS"
    a_count: int = Field(24, ge=0)
    b_count: int = Field(350, ge=0)
    c_count: int = Field(120, ge=0)
    d_count: int = Field(15000, ge=0)
    case_samples: Optional[List[Dict[str, Any]]] = None


@router.post("/studies/mine", status_code=status.HTTP_201_CREATED)
async def mine_pharmacovigilance_study(
    req: StudyMiningRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Executes statistical disproportionality signal mining (PRR, ROR, IC025) and stores study records."""
    repo = PVSignalMiningRepository(db)

    eval_res = engine.analyze_study(
        study_name=req.study_name,
        drug_name=req.drug_name,
        active_substance=req.active_substance,
        target_adverse_event=req.target_adverse_event,
        data_source=req.data_source,
        a_count=req.a_count,
        b_count=req.b_count,
        c_count=req.c_count,
        d_count=req.d_count,
        case_samples=req.case_samples,
    )

    study = await repo.create_study(
        study_name=eval_res["study_name"],
        drug_name=eval_res["drug_name"],
        active_substance=eval_res["active_substance"],
        target_adverse_event=eval_res["target_adverse_event"],
        data_source=eval_res["data_source"],
        total_cases_analyzed=eval_res["total_cases_analyzed"],
        signal_status=eval_res["signal_status"],
        who_causality_grade=eval_res["who_causality_grade"],
        study_summary_json=eval_res["study_summary_json"],
    )

    created_metrics = await repo.add_metrics(study.id, eval_res["metrics"])
    created_cases = await repo.add_case_reports(study.id, eval_res["case_reports"])

    return {
        "id": study.id,
        "study_name": study.study_name,
        "drug_name": study.drug_name,
        "active_substance": study.active_substance,
        "target_adverse_event": study.target_adverse_event,
        "data_source": study.data_source,
        "total_cases_analyzed": study.total_cases_analyzed,
        "signal_status": study.signal_status,
        "who_causality_grade": study.who_causality_grade,
        "summary": study.study_summary_json,
        "metrics": [
            {
                "metric_name": m.metric_name,
                "value": m.value,
                "confidence_interval_lower": m.confidence_interval_lower,
                "confidence_interval_upper": m.confidence_interval_upper,
                "is_statistically_significant": m.is_statistically_significant,
                "threshold_exceeded": m.threshold_exceeded,
            }
            for m in created_metrics
        ],
        "case_reports": [
            {
                "report_id": c.report_id,
                "patient_age": c.patient_age,
                "patient_gender": c.patient_gender,
                "primary_suspect_drug": c.primary_suspect_drug,
                "adverse_event_term": c.adverse_event_term,
                "meddra_soc": c.meddra_soc,
                "time_to_onset_days": c.time_to_onset_days,
                "outcome": c.outcome,
            }
            for c in created_cases
        ]
    }


@router.get("/studies")
async def list_studies(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists pharmacovigilance studies."""
    repo = PVSignalMiningRepository(db)
    studies = await repo.list_studies(limit=limit, offset=offset)
    return [
        {
            "id": s.id,
            "study_name": s.study_name,
            "drug_name": s.drug_name,
            "target_adverse_event": s.target_adverse_event,
            "data_source": s.data_source,
            "signal_status": s.signal_status,
            "who_causality_grade": s.who_causality_grade,
            "total_cases_analyzed": s.total_cases_analyzed,
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
    """Gets detailed pharmacovigilance study with disproportionality metrics and case reports."""
    repo = PVSignalMiningRepository(db)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Pharmacovigilance study not found")

    metrics = await repo.get_metrics_by_study(study_id)
    cases = await repo.get_cases_by_study(study_id)

    return {
        "id": study.id,
        "study_name": study.study_name,
        "drug_name": study.drug_name,
        "active_substance": study.active_substance,
        "target_adverse_event": study.target_adverse_event,
        "data_source": study.data_source,
        "total_cases_analyzed": study.total_cases_analyzed,
        "signal_status": study.signal_status,
        "who_causality_grade": study.who_causality_grade,
        "summary": study.study_summary_json,
        "metrics": [
            {
                "id": m.id,
                "metric_name": m.metric_name,
                "value": m.value,
                "confidence_interval_lower": m.confidence_interval_lower,
                "confidence_interval_upper": m.confidence_interval_upper,
                "is_statistically_significant": m.is_statistically_significant,
                "threshold_exceeded": m.threshold_exceeded,
            }
            for m in metrics
        ],
        "case_reports": [
            {
                "id": c.id,
                "report_id": c.report_id,
                "patient_age": c.patient_age,
                "patient_gender": c.patient_gender,
                "primary_suspect_drug": c.primary_suspect_drug,
                "concomitant_drugs": c.concomitant_drugs_json,
                "adverse_event_term": c.adverse_event_term,
                "meddra_soc": c.meddra_soc,
                "time_to_onset_days": c.time_to_onset_days,
                "outcome": c.outcome,
            }
            for c in cases
        ]
    }
