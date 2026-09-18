"""Tests for SyntheticGeneCircuitEngine."""

import pytest
from research.synbio.gene_circuit_engine import SyntheticGeneCircuitEngine


def test_synthetic_gene_circuit_and_gate_design():
    engine = SyntheticGeneCircuitEngine()
    design = engine.design_logic_circuit(
        circuit_name="Diagnostic_AND_Logic",
        logic_function="AND",
        chassis="Escherichia coli K-12",
        output_reporter="sfGFP",
    )
    assert design["circuit_name"] == "Diagnostic_AND_Logic"
    assert design["logic_function"] == "AND"
    assert design["on_off_dynamic_range"] >= 1.0
    assert len(design["gates"]) >= 2
    assert len(design["kinetics_traces"]) == 4  # 4 truth table states
    assert "assembly_plan" in design


def test_synthetic_gene_circuit_functions():
    engine = SyntheticGeneCircuitEngine()
    for fn in ["AND", "OR", "NOR", "NAND", "XOR"]:
        res = engine.design_logic_circuit(circuit_name=f"Test_{fn}", logic_function=fn)
        assert res["logic_function"] == fn
        assert len(res["gates"]) > 0
        assert len(res["kinetics_traces"]) == 4
