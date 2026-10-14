"""Tests for Phase 503: Autonomous Synthetic Protocellular Compartment Membraneless Coacervate-GUV Hybrid Bionanoreactor."""

import pytest
from research.orchestration.coacervate_guv_hybrid_bionanoreactor_engine import CoacervateGuvHybridBionanoreactorEngine


def test_coacervate_guv_hybrid_bionanoreactor_engine():
    engine = CoacervateGuvHybridBionanoreactorEngine()
    result = engine.analyze(
        target_specimen="Liquid-Liquid Phase Separated Polylysine-ATP Coacervates Encapsulated within POPC/Cholesterol Bilayer GUVs",
        analytical_modality="coacervate-guv-hybrid-reactor",
        input_scale=1.0,
    )

    assert result.target_specimen == "Liquid-Liquid Phase Separated Polylysine-ATP Coacervates Encapsulated within POPC/Cholesterol Bilayer GUVs"
    assert result.confidence_score >= 0.95
    assert result.enzyme_partition_coefficient_k_partition != 0.0
    assert result.internal_substrate_conversion_flux_uM_per_s != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Synthetic Protocell" in result.summary_report
