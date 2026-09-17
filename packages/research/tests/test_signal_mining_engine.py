"""Tests for PV Signal Mining Engine."""
import pytest
from research.pharmacovigilance.signal_mining_engine import PVSignalMiningEngine


def test_compute_contingency_matrix_confirmed_signal():
    engine = PVSignalMiningEngine()
    # A=45, B=1000, C=100, D=30000
    res = engine.compute_contingency_matrix(45, 1000, 100, 30000)

    assert res["signal_status"] == "CONFIRMED_SIGNAL"
    assert res["who_causality_grade"] == "PROBABLE"

    prr_metric = next(m for m in res["metrics"] if m["metric_name"] == "PRR")
    assert prr_metric["value"] >= 2.0
    assert prr_metric["is_statistically_significant"] is True

    ic_metric = next(m for m in res["metrics"] if m["metric_name"] == "IC025")
    assert ic_metric["value"] > 0.0


def test_compute_contingency_matrix_no_signal():
    engine = PVSignalMiningEngine()
    # A=1, B=5000, C=500, D=20000
    res = engine.compute_contingency_matrix(1, 5000, 500, 20000)

    assert res["signal_status"] == "NO_SIGNAL"
    assert res["who_causality_grade"] == "UNLIKELY"


def test_analyze_study_pipeline():
    engine = PVSignalMiningEngine()
    study = engine.analyze_study(
        study_name="GLP-1 Pancreatitis Study",
        drug_name="Semaglutide",
        active_substance="GLP-1 RA",
        target_adverse_event="Acute Pancreatitis",
        data_source="FAERS",
        a_count=30,
        b_count=1500,
        c_count=120,
        d_count=40000,
    )

    assert study["total_cases_analyzed"] == 41650
    assert study["signal_status"] in ["CONFIRMED_SIGNAL", "POTENTIAL_SIGNAL"]
    assert len(study["metrics"]) == 4
    assert len(study["case_reports"]) >= 1
