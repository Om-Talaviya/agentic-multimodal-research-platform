"""Tests for Phase 127 AntibodyAffinityMaturationEngine."""

import pytest
from research.immunology.antibody_maturation_engine import AntibodyAffinityMaturationEngine


def test_evaluate_mutation_energy():
    engine = AntibodyAffinityMaturationEngine()
    res = engine.evaluate_mutation_energy("CDR-H3", "Y", "TRP", 102, "PiStacking")
    assert res["cdr_region"] == "CDR-H3"
    assert res["predicted_ddg_kcal_mol"] < 0.0
    assert res["predicted_kd_nm"] < 10.0
    assert res["developability_pass"] is True


def test_simulate_maturation_campaign():
    engine = AntibodyAffinityMaturationEngine()
    res = engine.simulate_maturation_campaign(
        candidate_name="mAb-PanCorona-Neutralizer",
        target_antigen="SARS-CoV-2 Spike S1 RBD",
        parental_kd_nm=15.0,
    )
    assert res["candidate_name"] == "mAb-PanCorona-Neutralizer"
    assert res["matured_kd_nm"] < 1.0
    assert res["affinity_fold_improvement"] > 10.0
    assert len(res["top_variants"]) >= 4
    assert len(res["key_contacts"]) >= 3
    assert res["humanness_score_oasis"] >= 0.85
