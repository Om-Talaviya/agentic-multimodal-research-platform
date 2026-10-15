"""Tests for Phase 529: Autonomous Dissolution Dynamic Nuclear Polarization (DNP) Hyperpolarized Carbon-13 Flux Tracer."""

import pytest
from research.orchestration.magnetic_resonance_hyperpolarization_dnp_engine import MagneticResonanceHyperpolarizationDnpEngine


def test_magnetic_resonance_hyperpolarization_dnp_engine():
    engine = MagneticResonanceHyperpolarizationDnpEngine()
    result = engine.analyze(
        target_specimen="Hyperpolarized [1-13C] Pyruvate with Trityl Radical OX063 Polarized at 1.4K and 5T",
        analytical_modality="dnp-hyperpolarized-nmr-flux",
        input_scale=1.0,
    )

    assert result.target_specimen == "Hyperpolarized [1-13C] Pyruvate with Trityl Radical OX063 Polarized at 1.4K and 5T"
    assert result.confidence_score >= 0.95
    assert result.carbon_13_nuclear_polarization_pct != 0.0
    assert result.in_vivo_t1_relaxation_time_s != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Dissolution Dynamic" in result.summary_report
