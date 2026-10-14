"""Tests for Phase 512: Autonomous Single-Molecule Dual-Trap Optical Tweezers DNA Helicase Unwinding Stepper."""

import pytest
from research.orchestration.single_molecule_optical_trap_dna_helicase_engine import SingleMoleculeOpticalTrapDnaHelicaseEngine


def test_single_molecule_optical_trap_dna_helicase_engine():
    engine = SingleMoleculeOpticalTrapDnaHelicaseEngine()
    result = engine.analyze(
        target_specimen="Dual-Beam Optical Trap Tethered dsDNA Hairpin with Recombinant Human Bloom Syndrome Helicase",
        analytical_modality="optical-trap-helicase-unwinding",
        input_scale=1.0,
    )

    assert result.target_specimen == "Dual-Beam Optical Trap Tethered dsDNA Hairpin with Recombinant Human Bloom Syndrome Helicase"
    assert result.confidence_score >= 0.95
    assert result.helicase_stepping_velocity_bp_per_s != 0.0
    assert result.atp_fuel_efficiency_bp_per_atp != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Single-Molecule Dua" in result.summary_report
