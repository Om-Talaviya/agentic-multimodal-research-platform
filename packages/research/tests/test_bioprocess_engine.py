"""
Tests for Phase 62: Bioprocess Digital Twin Engine.
"""
from research.bioprocess.bioprocess_engine import BioprocessDigitalTwinEngine


def test_simulate_fed_batch_cycle():
    res = BioprocessDigitalTwinEngine.simulate_fed_batch_cycle(
        run_name="TestRun",
        cell_line="CHO-K1",
        volume_l=50.0,
    )
    assert "telemetry" in res
    assert "actions" in res
    assert len(res["telemetry"]) == 15
    assert res["final_titer"] > 0
