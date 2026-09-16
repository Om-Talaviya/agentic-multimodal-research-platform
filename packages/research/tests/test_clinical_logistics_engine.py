"""
Tests for Phase 63: Clinical Trial Logistics Engine.
"""
from research.logistics.clinical_logistics_engine import ClinicalTrialLogisticsEngine


def test_simulate_trial_logistics():
    res = ClinicalTrialLogisticsEngine.simulate_trial_logistics(
        protocol_no="PROTO-TEST",
        storage_regime="Ultra-Cold Chain (-80°C)",
    )
    assert "sites" in res
    assert "routes" in res
    assert len(res["sites"]) >= 4
    assert len(res["routes"]) >= 4
    assert res["global_risk"] > 0
