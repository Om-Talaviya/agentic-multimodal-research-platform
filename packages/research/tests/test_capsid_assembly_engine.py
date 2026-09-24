"""Tests for CapsidAssemblyEngine (Phase 151)."""

from research.virology.capsid_assembly_engine import (
    CapsidAssemblyEngine,
    CapsidAssemblyRequest,
)


def test_capsid_assembly_engine():
    engine = CapsidAssemblyEngine()
    req = CapsidAssemblyRequest(
        serotype_name="AAV-DJ Hybrid",
        ph_condition=7.2,
        temperature_celsius=37.0,
        vp1_vp2_vp3_ratio="1:1:10",
    )
    result = engine.simulate(req)
    assert result.assembly_yield_percent > 85.0
    assert result.gibbs_free_energy_kcal_mol < 0
    assert len(result.interfaces) == 3
    assert len(result.trajectories) == 4
