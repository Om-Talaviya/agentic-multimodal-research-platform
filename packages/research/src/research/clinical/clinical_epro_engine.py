"""Clinical Trial Decentralized ePRO & Real-World Outcomes Engine (Phase 141)."""

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class ePROSimulationRequest(BaseModel):
    protocol_id: str
    therapeutic_area: str
    patient_cohort_size: int = Field(default=100, ge=10)
    baseline_qol_score: float = Field(default=0.75, ge=0.0, le=1.0)
    trial_duration_weeks: int = Field(default=24, ge=4)


class PatientTelemetryPoint(BaseModel):
    patient_id: str
    visit_week: int
    vas_pain: float
    promis_fatigue: float
    eq5d_utility: float


class AEAlert(BaseModel):
    patient_id: str
    ctcae_grade: int
    symptom: str
    site_escalation: bool


class ePROSimulationResult(BaseModel):
    protocol_id: str
    therapeutic_area: str
    patients_enrolled: int
    overall_compliance_rate: float
    mean_qol_change_delta: float
    telemetry_samples: List[PatientTelemetryPoint]
    active_alerts: List[AEAlert]
    status: str = "COMPLETED"


class ClinicalePROEngine:
    """Analyzes decentralized clinical trial patient-reported outcomes and automated safety alerts."""

    def simulate(self, req: ePROSimulationRequest) -> ePROSimulationResult:
        compliance = 0.935
        delta_qol = round(0.12 * req.baseline_qol_score, 4)

        telemetry = []
        alerts = []

        for p_idx in range(min(5, req.patient_cohort_size)):
            pid = f"PT-{1000 + p_idx}"
            for w in [0, 4, 12, req.trial_duration_weeks]:
                vas = round(max(0.5, 4.2 - 0.1 * w + p_idx * 0.3), 1)
                fatigue = round(52.0 - 0.2 * w + p_idx * 1.5, 1)
                eq5d = round(min(1.0, req.baseline_qol_score + 0.005 * w - p_idx * 0.02), 2)
                telemetry.append(
                    PatientTelemetryPoint(
                        patient_id=pid,
                        visit_week=w,
                        vas_pain=vas,
                        promis_fatigue=fatigue,
                        eq5d_utility=eq5d,
                    )
                )

        # Generate sample safety alert
        alerts.append(
            AEAlert(
                patient_id="PT-1002",
                ctcae_grade=2,
                symptom="Severe Pruritus / Rash",
                site_escalation=True,
            )
        )
        alerts.append(
            AEAlert(
                patient_id="PT-1004",
                ctcae_grade=1,
                symptom="Mild Peripheral Neuropathy",
                site_escalation=False,
            )
        )

        return ePROSimulationResult(
            protocol_id=req.protocol_id,
            therapeutic_area=req.therapeutic_area,
            patients_enrolled=req.patient_cohort_size,
            overall_compliance_rate=compliance,
            mean_qol_change_delta=delta_qol,
            telemetry_samples=telemetry,
            active_alerts=alerts,
        )
