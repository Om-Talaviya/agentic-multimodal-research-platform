"""
Engine tests for Phase 166: MicroED Structural Engine.
"""

from research.structural.microed_structural_engine import MicroEDStructuralEngine


def test_microed_structural_engine():
    engine = MicroEDStructuralEngine()
    result = engine.simulate_microed_refinement(
        sample_name="Bovine Trypsin",
        voltage_kv=200.0,
        rotation_range=120.0,
        frames_count=5,
    )

    assert result.sample_name == "Bovine Trypsin"
    assert result.resolution_angstrom <= 1.0
    assert result.completeness_percent >= 90.0
    assert result.r_work < 0.20
    assert len(result.frames) == 5
    assert len(result.refinements) == 3
    assert len(result.recommendations) >= 2
