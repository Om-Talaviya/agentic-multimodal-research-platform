"""Tests for Phase 445: Autonomous High-Density Solid-Phase Peptide Synthesis (SPPS) Coupling Yield & Aggregation Engine."""

import pytest
from research.orchestration.solid_phase_peptide_synthesis_coupling_engine import SolidPhasePeptideSynthesisEngine


def test_solid_phase_peptide_synthesis_coupling_engine():
    engine = SolidPhasePeptideSynthesisEngine()
    result = engine.analyze(
        target_specimen="40-Mer Hydrophobic Amyloid-Beta Peptide Intermediate on Wang Resin Microbeads",
        analytical_modality="solid-phase-peptide-synthesis",
        input_scale=1.0,
    )

    assert result.target_specimen == "40-Mer Hydrophobic Amyloid-Beta Peptide Intermediate on Wang Resin Microbeads"
    assert result.confidence_score >= 0.95
    assert result.fmoc_deprotection_efficiency_ratio > 0.0
    assert result.coupling_reaction_half_life_seconds > 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous High-Density Solid-" in result.summary_report
