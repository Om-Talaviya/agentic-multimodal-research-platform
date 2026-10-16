"""Tests for Phase 558: Autonomous Single-Molecule Mechanical Force Spectroscopy Chromatin Fiber Nucleosome Unwrapping Modeler."""

import pytest
from research.orchestration.single_molecule_chromatin_nucleosome_unwrapping_engine import SingleMoleculeChromatinNucleosomeUnwrappingEngine


def test_single_molecule_chromatin_nucleosome_unwrapping_engine():
    engine = SingleMoleculeChromatinNucleosomeUnwrappingEngine()
    result = engine.analyze(
        target_specimen="Reconstituted 12-Nucleosome Chromatin Array with Widom 601 positioning sequences stretched via Dual-Beam Optical Tweezers",
        analytical_modality="chromatin-force-spectroscopy",
        input_scale=1.0,
    )

    assert result.target_specimen == "Reconstituted 12-Nucleosome Chromatin Array with Widom 601 positioning sequences stretched via Dual-Beam Optical Tweezers"
    assert result.confidence_score >= 0.95
    assert result.outer_turn_unwrapping_force_threshold_pn != 0.0
    assert result.inner_turn_cooperative_rupture_force_pn != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Single-Molecule Mec" in result.summary_report
