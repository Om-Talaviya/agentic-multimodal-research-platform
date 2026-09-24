"""Tests for PROTACKineticsEngine (Phase 156)."""

from research.targeted_degradation.protac_kinetics_engine import (
    PROTACKineticsEngine,
    PROTACKineticsRequest,
)


def test_protac_kinetics_engine():
    engine = PROTACKineticsEngine()
    req = PROTACKineticsRequest(
        protac_compound_name="MZ1 (BRD4 Degrader)",
        target_protein_name="BRD4 BD1/BD2",
        e3_ligase_name="VHL",
        linker_type="PEG4 Linker",
        target_kd_binary_nM=20.0,
        e3_kd_binary_nM=40.0,
    )
    result = engine.simulate_degradation(req)
    assert result.cooperativity_alpha > 1.0
    assert result.dc50_nM > 0
    assert result.dmax_percent > 80.0
    assert len(result.e3_profiles) == 2
    assert len(result.dose_response_curve) >= 5
