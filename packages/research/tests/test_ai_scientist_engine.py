"""Tests for Autonomous Scientist Engine (Phase 50)."""
from research.ai_scientist_engine import AutonomousScientistEngine

def test_ai_scientist_engine():
    engine = AutonomousScientistEngine()
    res = engine.run_autonomous_program(
        title="Pan-KRAS Autonomous Discovery",
        domain="Structural Oncology",
        goal="Discover resistance-free degraders",
        cycles_count=3
    )
    assert len(res["cycles"]) == 3
    assert res["overall_novelty"] > 0.90
    assert res["breakthrough"]["breakthrough_class"] == "NOBEL_TURING_CLASS"
    assert res["breakthrough"]["novelty_score"] > 0.90
