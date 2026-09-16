"""
Tests for Phase 58: PPI Engine.
"""
from research.ppi.ppi_engine import PPIInteractomeEngine


def test_generate_interactome():
    res = PPIInteractomeEngine.generate_interactome(
        seed_gene="KRAS",
        disease_context="Pancreatic Cancer",
    )
    assert "nodes" in res
    assert "edges" in res
    assert len(res["nodes"]) >= 5
    assert len(res["edges"]) >= 5
