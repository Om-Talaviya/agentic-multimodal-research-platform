"""
Tests for Clinical Trial Optimizer Engine.
"""
from research.clinical_trial_engine import ClinicalTrialOptimizerEngine

def test_clinical_trial_optimizer_engine():
    engine = ClinicalTrialOptimizerEngine()
    res = engine.optimize_protocol(
        title="Phase II Melanoma AGY-900",
        indication="Metastatic Melanoma",
        agent="AGY-900",
        phase="Phase II",
        target_power=0.85
    )
    assert res["sample_size_target"] > 50
    assert len(res["criteria"]) >= 4
    assert len(res["patients"]) == 10
    assert res["synthetic_arm"]["hazard_ratio"] < 1.0
    assert len(res["synthetic_arm"]["survival_curve"]) > 5
