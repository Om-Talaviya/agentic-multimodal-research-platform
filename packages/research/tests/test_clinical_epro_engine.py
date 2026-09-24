"""Tests for ClinicalePROEngine."""

from research.clinical.clinical_epro_engine import (
    ClinicalePROEngine,
    ePROSimulationRequest,
)


def test_clinical_epro_engine():
    engine = ClinicalePROEngine()
    req = ePROSimulationRequest(
        protocol_id="NEURO-AD-003",
        therapeutic_area="Alzheimer's Disease",
        patient_cohort_size=80,
        baseline_qol_score=0.68,
        trial_duration_weeks=52,
    )
    res = engine.simulate(req)
    assert res.status == "COMPLETED"
    assert res.overall_compliance_rate > 0.90
    assert len(res.telemetry_samples) > 0
    assert len(res.active_alerts) == 2
