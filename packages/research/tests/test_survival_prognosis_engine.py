"""
Unit tests for Phase 110: Survival Prognosis Engine.
"""
import pytest
from research.clinical.survival_prognosis_engine import SurvivalPrognosisEngine

def test_kaplan_meier_estimation():
    engine = SurvivalPrognosisEngine()

    times = [6.0, 12.0, 18.0, 24.0, 30.0]
    events = [1, 1, 0, 1, 1]

    km = engine.compute_kaplan_meier(times, events)
    assert len(km["time_points"]) > 1
    assert km["survival_prob"][0] == 1.0
    assert km["survival_prob"][-1] < 1.0

def test_c_index_calculation():
    engine = SurvivalPrognosisEngine()

    # Higher risk score -> lower survival time (perfect concordance)
    risk_scores = [3.0, 2.0, 1.0, 0.5]
    times = [10.0, 20.0, 30.0, 40.0]
    events = [1, 1, 1, 1]

    c_index = engine.compute_c_index(risk_scores, times, events)
    assert c_index == 1.0

def test_cohort_simulation():
    engine = SurvivalPrognosisEngine()

    result = engine.simulate_cohort_prognosis(
        model_name="Pan-Cancer-Stratifier",
        cancer_cohort="TCGA-LUAD",
        sample_size=60
    )

    assert result["model_name"] == "Pan-Cancer-Stratifier"
    assert len(result["patients"]) == 60
    assert len(result["curves"]) == 3
    assert result["c_index_score"] >= 0.80
    assert result["summary"]["high_risk_count"] > 0
