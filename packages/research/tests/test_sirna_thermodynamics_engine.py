"""Tests for siRNA Thermodynamics Engine."""

import pytest
from research.rnai.sirna_thermodynamics_engine import SiRNAThermodynamicsEngine


def test_sirna_thermodynamics_engine_evaluation() -> None:
    engine = SiRNAThermodynamicsEngine()
    result = engine.evaluate_sirna_thermodynamics(
        study_name="TP53 siRNA Knockdown Campaign",
        target_mrna_transcript="NM_000546.6 (TP53)",
        target_gene="TP53",
    )

    assert result["study_name"] == "TP53 siRNA Knockdown Campaign"
    assert result["candidates_screened"] == 4
    assert len(result["duplexes"]) == 4
    assert len(result["off_targets"]) >= 1
    assert result["best_candidate_guide_strand"] != ""
    assert result["mean_on_target_efficiency"] > 50.0

    # Validate asymmetric thermodynamics
    first_duplex = result["duplexes"][0]
    assert "delta_delta_g_asymmetry" in first_duplex
    assert "risc_loading_preference" in first_duplex
    assert "seed_region_tm_celsius" in first_duplex
