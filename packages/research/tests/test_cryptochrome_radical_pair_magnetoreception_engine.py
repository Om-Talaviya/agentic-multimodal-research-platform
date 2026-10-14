"""Tests for Phase 493: Autonomous Quantum Coherent Magnetoreception Cryptochrome Radical Pair Dynamics Simulator."""

import pytest
from research.orchestration.cryptochrome_radical_pair_magnetoreception_engine import CryptochromeRadicalPairMagnetoreceptionEngine


def test_cryptochrome_radical_pair_magnetoreception_engine():
    engine = CryptochromeRadicalPairMagnetoreceptionEngine()
    result = engine.analyze(
        target_specimen="Purified Migratory Avian Cryptochrome-4 (ErCry4) Flavin-Tryptophan Photoreduced Radical Pair",
        analytical_modality="quantum-radical-pair-magnetoreception",
        input_scale=1.0,
    )

    assert result.target_specimen == "Purified Migratory Avian Cryptochrome-4 (ErCry4) Flavin-Tryptophan Photoreduced Radical Pair"
    assert result.confidence_score >= 0.95
    assert result.singlet_triplet_yield_anisotropy_ratio != 0.0
    assert result.radical_pair_quantum_coherence_time_us != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Quantum Coherent Ma" in result.summary_report
