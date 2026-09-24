"""Tests for AptamerEvolutionEngine."""

from research.nucleic.aptamer_evolution_engine import (
    AptamerEvolutionEngine,
    SELEXEvolutionRequest,
)


def test_aptamer_evolution_engine():
    engine = AptamerEvolutionEngine()
    req = SELEXEvolutionRequest(
        target_protein_name="VEGF165",
        aptamer_type="RNA",
        target_pka=8.2,
        selection_rounds=6,
        random_region_length=35,
    )
    res = engine.evolve(req)
    assert res.status == "COMPLETED"
    assert res.total_rounds_simulated == 6
    assert len(res.evolution_trajectory) == 6
    assert res.top_lead.kd_nm < 100.0
    assert len(res.consensus_motif) > 5
