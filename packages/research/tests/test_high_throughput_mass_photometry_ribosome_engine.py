"""Tests for Phase 516: Autonomous Automated High-Throughput Mass Photometry Macromolecular Mass Dispersity Profiler."""

import pytest
from research.orchestration.high_throughput_mass_photometry_ribosome_engine import HighThroughputMassPhotometryRibosomeEngine


def test_high_throughput_mass_photometry_ribosome_engine():
    engine = HighThroughputMassPhotometryRibosomeEngine()
    result = engine.analyze(
        target_specimen="Label-Free Reconstituted 70S Ribosome Assembly Intermediates with Initiation Factors IF1/IF2/IF3",
        analytical_modality="mass-photometry-single-molecule-scattering",
        input_scale=1.0,
    )

    assert result.target_specimen == "Label-Free Reconstituted 70S Ribosome Assembly Intermediates with Initiation Factors IF1/IF2/IF3"
    assert result.confidence_score >= 0.95
    assert result.molecular_mass_resolution_error_pct != 0.0
    assert result.subassembly_stoichiometric_ratio_30s_50s_70s != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Automated High-Thro" in result.summary_report
