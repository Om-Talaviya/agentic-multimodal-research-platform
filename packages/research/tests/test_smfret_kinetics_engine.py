"""Tests for smFRETKineticsEngine (Phase 160)."""

from research.biophysics.smfret_kinetics_engine import (
    smFRETKineticsEngine,
    smFRETRequest,
)


def test_smfret_kinetics_engine():
    engine = smFRETKineticsEngine()
    req = smFRETRequest(
        biomolecule_name="Ribosome Translation Complex",
        donor_fluorophore="Cy3",
        acceptor_fluorophore="Cy5",
        laser_power_mw=15.0,
        sampling_rate_hz=100.0,
    )
    result = engine.analyze_traces(req)
    assert result.molecules_analyzed_count > 0
    assert 0.0 <= result.mean_fret_efficiency <= 1.0
    assert len(result.conformational_states) == 3
    assert len(result.sample_time_traces) == 3
