"""Tests for Phase 564: Autonomous Acoustic Micro-Streaming Single-Cell Intracellular Delivery Sonoporation Engine."""

import pytest
from research.orchestration.acoustic_microstreaming_sonoporation_engine_engine import AcousticMicrostreamingSonoporationEngineEngine


def test_acoustic_microstreaming_sonoporation_engine_engine():
    engine = AcousticMicrostreamingSonoporationEngineEngine()
    result = engine.analyze(
        target_specimen="Suspended Human CD34+ Hematopoietic Stem Cells and Phospholipid Microbubbles subjected to 1-MHz Focused Acoustic Waves",
        analytical_modality="acoustic-microstreaming-sonoporation",
        input_scale=1.0,
    )

    assert result.target_specimen == "Suspended Human CD34+ Hematopoietic Stem Cells and Phospholipid Microbubbles subjected to 1-MHz Focused Acoustic Waves"
    assert result.confidence_score >= 0.95
    assert result.intracellular_delivery_efficiency_pct != 0.0
    assert result.cell_membrane_resealing_time_seconds != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Acoustic Micro-Stre" in result.summary_report
