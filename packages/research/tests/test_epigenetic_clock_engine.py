"""Tests for EpigeneticClockEngine."""

import pytest
from research.epigenetics.epigenetic_clock_engine import EpigeneticClockEngine


def test_epigenetic_clock_prediction_horvath():
    engine = EpigeneticClockEngine()
    betas = {
        "cg00075967": 0.72,
        "cg16867657": 0.65,
        "cg09809672": 0.40,
        "cg22454769": 0.80,
    }
    res = engine.predict_age(chronological_age=50.0, beta_values=betas, clock_model="Horvath")
    assert "predicted_epigenetic_age" in res
    assert "age_acceleration" in res
    assert res["clock_model"] == "Horvath"
    assert res["cpgs_utilized"] >= 10
    assert "confidence_interval" in res
    assert res["confidence_interval"]["low"] <= res["predicted_epigenetic_age"] <= res["confidence_interval"]["high"]
    assert 0.0 <= res["mortality_risk_percentile"] <= 100.0
    assert len(res["top_cpg_markers"]) > 0


def test_epigenetic_clock_models():
    engine = EpigeneticClockEngine()
    for model_name in ["Horvath", "Hannum", "PhenoAge", "GrimAge"]:
        res = engine.predict_age(chronological_age=30.0, beta_values={}, clock_model=model_name)
        assert res["clock_model"] == model_name
        assert res["predicted_epigenetic_age"] >= 0.0
        assert res["pace_of_aging"] > 0.0
