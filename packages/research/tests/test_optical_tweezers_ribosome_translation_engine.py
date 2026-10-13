"""Tests for Phase 451: Autonomous Single-Molecule Optical Tweezers Ribosome Translation Kinetic Polypeptide Translocation Engine."""

import pytest
from research.orchestration.optical_tweezers_ribosome_translation_engine import OpticalTweezersRibosomeTranslationEngine


def test_optical_tweezers_ribosome_translation_engine():
    engine = OpticalTweezersRibosomeTranslationEngine()
    result = engine.analyze(
        target_specimen="70S Bacterial Ribosome Translating Structured mRNA Stem-Loop under Constant Force (12 pN)",
        analytical_modality="ribosome-translation-dynamics",
        input_scale=1.0,
    )

    assert result.target_specimen == "70S Bacterial Ribosome Translating Structured mRNA Stem-Loop under Constant Force (12 pN)"
    assert result.confidence_score >= 0.95
    assert result.codon_stepping_dwell_time_ms != 0.0
    assert result.mrna_unfolding_barrier_activation_energy_kb_t != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Single-Molecule Opt" in result.summary_report
