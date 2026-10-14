"""Tests for Phase 506: Autonomous DNA Origami Reconfigurable Plasmonic Nanoruler Distance Calibrator."""

import pytest
from research.orchestration.dna_origami_plasmonic_nanoruler_engine import DnaOrigamiPlasmonicNanorulerEngine


def test_dna_origami_plasmonic_nanoruler_engine():
    engine = DnaOrigamiPlasmonicNanorulerEngine()
    result = engine.analyze(
        target_specimen="Scaffolded DNA Origami 12-Helix Bundle with Gold Nanoparticle Dimer Heterostructure",
        analytical_modality="dna-origami-plasmonic-nanoruler",
        input_scale=1.0,
    )

    assert result.target_specimen == "Scaffolded DNA Origami 12-Helix Bundle with Gold Nanoparticle Dimer Heterostructure"
    assert result.confidence_score >= 0.95
    assert result.plasmonic_coupling_resonance_wavelength_nm != 0.0
    assert result.interparticle_gap_distance_nm != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous DNA Origami Reconfi" in result.summary_report
