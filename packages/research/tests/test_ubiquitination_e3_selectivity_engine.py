"""Tests for Phase 207: Proteome-Wide Ubiquitination & E3 Ligase Selectivity Engine Engine."""

import pytest
from research.proteomics.ubiquitination_e3_selectivity_engine import UbiquitinationE3SelectivityEngine


def test_ubiquitination_e3_selectivity_engine():
    engine = UbiquitinationE3SelectivityEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Ubiquitination E3 Selectivity",
        input_scale=1.0,
    )
    assert getattr(result, "ubiquitination_site_prediction_auroc") != 0
    assert getattr(result, "e3_ligase_selectivity_binding_affinity_kd_nm") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
