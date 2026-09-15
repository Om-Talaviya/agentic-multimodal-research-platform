"""Tests for Pathway Perturbation Engine (Phase 48)."""
from research.pathway_perturbation_engine import PathwayPerturbationEngine

def test_pathway_perturbation_engine():
    engine = PathwayPerturbationEngine()
    res = engine.simulate_perturbation(
        title="EGFR Knockdown Simulation",
        target_node="EGFR",
        cell_line="PC9",
        perturbation_type="SMALL_MOLECULE",
        time_course_hours=48
    )
    assert res["cascade"]["node_count"] > 10
    assert len(res["simulation"]["trajectories"]) == 13
    assert res["simulation"]["inhibition_efficiency"] > 90.0
    assert len(res["simulation"]["bypass_mechanisms"]) >= 2
