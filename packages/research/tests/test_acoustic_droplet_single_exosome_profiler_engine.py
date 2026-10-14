"""Tests for Phase 502: Autonomous Microfluidic Acoustic Sorting & Droplet Single-Exosome Surface Tetraspanin Profiler."""

import pytest
from research.orchestration.acoustic_droplet_single_exosome_profiler_engine import AcousticDropletSingleExosomeProfilerEngine


def test_acoustic_droplet_single_exosome_profiler_engine():
    engine = AcousticDropletSingleExosomeProfilerEngine()
    result = engine.analyze(
        target_specimen="Surface Acoustic Wave (SAW) Focused Patient Plasma with CD63/CD81/CD9 Fluorophore Micro-Beads",
        analytical_modality="acoustic-droplet-single-exosome",
        input_scale=1.0,
    )

    assert result.target_specimen == "Surface Acoustic Wave (SAW) Focused Patient Plasma with CD63/CD81/CD9 Fluorophore Micro-Beads"
    assert result.confidence_score >= 0.95
    assert result.exosome_acoustic_separation_purity_pct != 0.0
    assert result.droplet_single_vesicle_encapsulation_lambda != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Microfluidic Acoust" in result.summary_report
