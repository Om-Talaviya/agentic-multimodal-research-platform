"""Tests for Phase 253: Autonomous Single-Molecule FISH Subcellular RNA Transcript Localization & Cluster Analysis Engine Engine."""

import pytest
from research.orchestration.smfish_subcellular_rna_localization_engine import SmfishSubcellularRnaLocalizationEngine


def test_smfish_subcellular_rna_localization_engine():
    engine = SmfishSubcellularRnaLocalizationEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="smfish-subcellular-rna-localization",
        input_scale=1.0,
    )
    assert getattr(result, "psf_localization_precision_nm") != 0
    assert getattr(result, "subcellular_clustering_ripleys_k_score") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
