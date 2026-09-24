"""FastAPI Route for Clinical Trial ePRO (Phase 141)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.clinical_epro_repo import ClinicalePRORepository
from research.clinical.clinical_epro_engine import (
    ClinicalePROEngine,
    ePROSimulationRequest,
    ePROSimulationResult,
)

router = APIRouter(prefix="/clinical-epro", tags=["Clinical ePRO"])


@router.post("/simulate", response_model=ePROSimulationResult)
async def simulate_epro_protocol(
    payload: ePROSimulationRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = ClinicalePROEngine()
    result = engine.simulate(payload)

    repo = ClinicalePRORepository(db)
    study = await repo.create_study(
        protocol_id=result.protocol_id,
        therapeutic_area=result.therapeutic_area,
        patient_count=result.patients_enrolled,
        compliance_rate=result.overall_compliance_rate,
        composite_qol_score=result.mean_qol_change_delta,
    )

    for pt in result.telemetry_samples:
        await repo.add_survey_telemetry(
            study_id=study.id,
            patient_pseudonym=pt.patient_id,
            visit_day=pt.visit_week * 7,
            vas_pain_score=pt.vas_pain,
            promis_fatigue_score=pt.promis_fatigue,
            eq5d_utility_index=pt.eq5d_utility,
        )

    for ae in result.active_alerts:
        await repo.add_adverse_event_alert(
            study_id=study.id,
            patient_pseudonym=ae.patient_id,
            ctcae_grade=ae.ctcae_grade,
            symptom_name=ae.symptom,
            requires_site_escalation=ae.site_escalation,
        )

    return result
