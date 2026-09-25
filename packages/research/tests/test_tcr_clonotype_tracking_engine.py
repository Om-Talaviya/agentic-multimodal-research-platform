"""Tests for TCR/BCR Clonotype Tracking Engine."""

import pytest
from research.immunology.tcr_clonotype_tracking_engine import TCRClonotypeTrackingEngine


def test_tcr_clonotype_engine_diversity_and_lineage() -> None:
    engine = TCRClonotypeTrackingEngine()

    freqs = [0.30, 0.20, 0.15, 0.10, 0.05]
    div = engine.calculate_repertoire_diversity(freqs)

    assert div["shannon_entropy"] > 0.0
    assert 0.0 <= div["clonality_score"] <= 1.0
    assert div["gini_simpson_index"] > 0.0

    res = engine.analyze_clonotype_lineage(
        study_name="In-Vitro Clone Tracking",
        sample_source="PBMC",
        repertoire_type="TCR_alpha_beta",
    )

    assert res["study_name"] == "In-Vitro Clone Tracking"
    assert len(res["clonotypes"]) == 5
    assert len(res["diversity_metrics"]) == 4
    assert res["clonotypes"][0]["expansion_status"] == "hyperexpanded"
