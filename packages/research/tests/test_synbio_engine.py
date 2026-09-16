"""
Tests for Phase 65: Synthetic Biology Engine.
"""
from research.synbio.synbio_engine import SyntheticBiologyEngine


def test_compile_circuit():
    res = SyntheticBiologyEngine.compile_circuit(
        circuit_name="TestGate",
        logic_expression="A AND B",
    )
    assert "parts" in res
    assert "truth_table" in res
    assert len(res["parts"]) >= 4
    assert len(res["truth_table"]) == 4
    assert res["on_off_ratio"] > 10.0
