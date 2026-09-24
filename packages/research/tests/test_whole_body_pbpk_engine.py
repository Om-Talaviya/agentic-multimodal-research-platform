"""Tests for Whole-Body PBPK Research Engine."""

import pytest
from research.pbpk.whole_body_pbpk_engine import WholeBodyPBPKEngine


def test_whole_body_pbpk_engine_simulation() -> None:
    engine = WholeBodyPBPKEngine()

    kp = engine.calculate_partition_coefficient(logp=2.5, unbound_fraction=0.08, lipid_fraction=0.035)
    assert kp > 0.0

    res = engine.simulate_pharmacokinetics(
        study_name="Preclinical PBPK Model",
        drug_candidate_name="CMPD-101",
        molecular_weight_da=450.0,
        logp=2.5,
        plasma_protein_unbound_fraction=0.08,
        intrinsic_clearance_ml_min_kg=15.0,
        species="human",
        administration_route="oral",
        dose_mg_kg=10.0,
        simulation_time_hours=24.0,
    )

    assert res["study_name"] == "Preclinical PBPK Model"
    assert "summary_metrics" in res
    assert res["summary_metrics"]["steady_state_volume_of_distribution_l_kg"] > 0
    assert len(res["compartments"]) == 9
    assert len(res["clearance_rates"]) == 2
