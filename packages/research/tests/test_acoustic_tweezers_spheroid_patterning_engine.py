"""Tests for Phase 465: Autonomous Microfluidic Acoustic Tweezers Multicellular Spheroid Patterning & Cytoskeletal Stress Engine."""

import pytest
from research.orchestration.acoustic_tweezers_spheroid_patterning_engine import AcousticTweezersSpheroidPatterningEngine


def test_acoustic_tweezers_spheroid_patterning_engine():
    engine = AcousticTweezersSpheroidPatterningEngine()
    result = engine.analyze(
        target_specimen="3D MCF-7 Breast Tumor Spheroid Array patterned in 2.5 MHz Standing Bulk Acoustic Wave Resonator",
        analytical_modality="acoustic-spheroid-patterning",
        input_scale=1.0,
    )

    assert result.target_specimen == "3D MCF-7 Breast Tumor Spheroid Array patterned in 2.5 MHz Standing Bulk Acoustic Wave Resonator"
    assert result.confidence_score >= 0.95
    assert result.acoustic_radiation_force_pN != 0.0
    assert result.spheroid_diameter_uniformity_cv != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Microfluidic Acoust" in result.summary_report
