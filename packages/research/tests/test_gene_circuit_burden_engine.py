import pytest
from research.circuits.burden_engine import GeneCircuitBurdenEngine

def test_gene_circuit_burden_engine():
    engine = GeneCircuitBurdenEngine()

    # 1. Test balanced circuit simulation
    res = engine.simulate_circuit_metabolic_burden(
        circuit_name="Inverter-Gate",
        promoter_strength_rpum=1000.0,
        cds_length_amino_acids=400,
        copy_number_per_cell=10,
        host_organism="E. coli K-12",
    )
    assert 0.0 <= res["ribosome_allocation_pct"] <= 100.0
    assert 0.0 <= res["growth_rate_penalty_pct"] <= 100.0
    assert res["evolutionary_half_life_generations"] > 10.0
    assert res["metabolic_burden_status"] in ["OPTIMAL", "BALANCED", "SEVERE_BURDEN"]
