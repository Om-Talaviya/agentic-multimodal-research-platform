"""Tests for Phase 533: Autonomous DNA Origami Plasmonic Hotspot Nanopore Single-Molecule Optical Tweezers Integrator."""

import pytest
from research.orchestration.dna_origami_plasmonic_nanopore_hybrid_engine import DnaOrigamiPlasmonicNanoporeHybridEngine


def test_dna_origami_plasmonic_nanopore_hybrid_engine():
    engine = DnaOrigamiPlasmonicNanoporeHybridEngine()
    result = engine.analyze(
        target_specimen="Hybrid Gold Bowtie Nanoantenna Mounted on 3D DNA Origami Funnel over 5nm Solid-State Nanopore",
        analytical_modality="plasmonic-nanopore-optical-tweezers",
        input_scale=1.0,
    )

    assert result.target_specimen == "Hybrid Gold Bowtie Nanoantenna Mounted on 3D DNA Origami Funnel over 5nm Solid-State Nanopore"
    assert result.confidence_score >= 0.95
    assert result.optical_trapping_stiffness_fN_nm_mW != 0.0
    assert result.electromagnetic_hotspot_field_enhancement != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous DNA Origami Plasmon" in result.summary_report
