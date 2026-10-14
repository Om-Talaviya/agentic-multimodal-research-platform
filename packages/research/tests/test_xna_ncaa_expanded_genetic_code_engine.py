"""Tests for Phase 498: Autonomous Xenobiotic Non-Canonical Amino Acid Expanded Genetic Code Ribosome Translator."""

import pytest
from research.orchestration.xna_ncaa_expanded_genetic_code_engine import XnaNcaaExpandedGeneticCodeEngine


def test_xna_ncaa_expanded_genetic_code_engine():
    engine = XnaNcaaExpandedGeneticCodeEngine()
    result = engine.analyze(
        target_specimen="Orthogonal Methionyl-tRNA Synthetase / tRNA Pair in Recoded E. coli C321.deltaA with UAG Amber Suppression",
        analytical_modality="expanded-genetic-code-translation",
        input_scale=1.0,
    )

    assert result.target_specimen == "Orthogonal Methionyl-tRNA Synthetase / tRNA Pair in Recoded E. coli C321.deltaA with UAG Amber Suppression"
    assert result.confidence_score >= 0.95
    assert result.ncaa_incorporation_fidelity_pct != 0.0
    assert result.amber_uag_suppression_efficiency != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Xenobiotic Non-Cano" in result.summary_report
