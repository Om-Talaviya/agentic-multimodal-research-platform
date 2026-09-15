"""Unit tests for Super-Graph Engine (Phase 44)."""
import pytest
from research.super_graph_engine import SuperGraphHypothesisEngine

def test_super_graph_engine():
    engine = SuperGraphHypothesisEngine(seed=123)

    seed = engine.generate_seed_supergraph()
    assert "nodes" in seed
    assert "edges" in seed
    assert len(seed["nodes"]) >= 6
    assert len(seed["edges"]) >= 5

    hypotheses = engine.formulate_causal_hypotheses(focus_entity="PCSK9")
    assert len(hypotheses) >= 2
    assert "title" in hypotheses[0]
    assert len(hypotheses[0]["mechanistic_chain"]) >= 3
    assert hypotheses[0]["novelty_score"] > 0.8
