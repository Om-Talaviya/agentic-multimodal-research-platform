"""Tests for Clinical Site Selection Engine."""
import pytest
from research.clinical.site_selection_engine import ClinicalSiteSelectionEngine


def test_evaluate_site_high_velocity():
    engine = ClinicalSiteSelectionEngine()
    site_input = {
        "site_name": "Prime Medical Center",
        "country": "USA",
        "city": "Boston",
        "principal_investigator": "Dr. House",
        "historical_recruitment_rate": 3.5,
        "ethics_approval_timeline_days": 30,
        "patient_pool_density": 4500,
        "pi_experience_years": 12.0,
        "competing_trials_count": 1,
    }

    result = engine.evaluate_site(site_input)
    assert result["feasibility_score"] >= 0.75
    assert result["risk_tier"] == "LOW_RISK"
    assert result["selected_for_trial"] is True
    assert "metrics_json" in result


def test_evaluate_site_low_velocity():
    engine = ClinicalSiteSelectionEngine()
    site_input = {
        "site_name": "Rural Clinic",
        "country": "Country X",
        "city": "Town Y",
        "principal_investigator": "Dr. Novice",
        "historical_recruitment_rate": 0.3,
        "ethics_approval_timeline_days": 90,
        "patient_pool_density": 400,
        "pi_experience_years": 2.0,
        "competing_trials_count": 5,
    }

    result = engine.evaluate_site(site_input)
    assert result["feasibility_score"] < 0.50
    assert result["risk_tier"] == "HIGH_RISK"
    assert result["selected_for_trial"] is False


def test_simulate_recruitment():
    engine = ClinicalSiteSelectionEngine()
    sites = [
        {"historical_recruitment_rate": 2.5, "ethics_approval_timeline_days": 35, "selected_for_trial": True},
        {"historical_recruitment_rate": 2.0, "ethics_approval_timeline_days": 40, "selected_for_trial": True},
    ]

    sim = engine.simulate_recruitment(
        target_enrollment=100,
        recruitment_duration_months=12.0,
        sites=sites,
        dropout_rate=0.10,
    )

    assert sim["p10_completion_months"] <= sim["p50_completion_months"] <= sim["p90_completion_months"]
    assert len(sim["enrollment_curve_json"]) > 0
    assert "bottleneck_risks_json" in sim


def test_evaluate_study_feasibility_pipeline():
    engine = ClinicalSiteSelectionEngine()
    study_data = {
        "study_title": "Phase 2 Pancreatic Adenocarcinoma",
        "protocol_code": "PDAC-202",
        "indication": "Pancreatic Cancer",
        "phase": "Phase 2",
        "target_enrollment": 120,
        "recruitment_duration_months": 14.0,
    }
    sites = [
        {"site_name": "Site 1", "country": "USA", "city": "NY", "principal_investigator": "Dr. A", "historical_recruitment_rate": 2.5},
        {"site_name": "Site 2", "country": "UK", "city": "London", "principal_investigator": "Dr. B", "historical_recruitment_rate": 1.8},
    ]

    res = engine.evaluate_study_feasibility(study_data, sites)
    assert res["total_sites"] == 2
    assert len(res["evaluated_sites"]) == 2
    assert res["simulation"]["target_timeline_months"] == 14.0
