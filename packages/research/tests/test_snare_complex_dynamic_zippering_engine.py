"""Tests for Phase 487: Autonomous Synaptic Vesicle SNARE Complex Dynamic Zippering & Neurotransmitter Release Predictor."""

import pytest
from research.orchestration.snare_complex_dynamic_zippering_engine import SnareComplexDynamicZipperingEngine


def test_snare_complex_dynamic_zippering_engine():
    engine = SnareComplexDynamicZipperingEngine()
    result = engine.analyze(
        target_specimen="Reconstituted Proteoliposome Single-Vesicle Synaptobrevin-2 / Syntaxin-1A / SNAP-25 Assembly",
        analytical_modality="snare-complex-zippering",
        input_scale=1.0,
    )

    assert result.target_specimen == "Reconstituted Proteoliposome Single-Vesicle Synaptobrevin-2 / Syntaxin-1A / SNAP-25 Assembly"
    assert result.confidence_score >= 0.95
    assert result.snare_zippering_free_energy_kbT != 0.0
    assert result.membrane_fusion_pore_opening_time_ms != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Synaptic Vesicle SN" in result.summary_report
