"""Tests for Phase 132 ViralPhylodynamicsEngine."""

import pytest
from research.epidemiology.viral_phylodynamics_engine import (
    ViralPhylodynamicsEngine,
    LineageSeed,
)


def test_viral_phylodynamics_simulation_flow():
    engine = ViralPhylodynamicsEngine()

    seeds = [
        LineageSeed(
            clade_name="23I (Omicron)",
            pangolin_designation="BA.2.86",
            who_label="Pirola",
            defining_mutations=["S:K356T", "S:V483del"],
            initial_proportion=0.35,
            fitness_advantage=0.04,
        ),
        LineageSeed(
            clade_name="24A (JN.1)",
            pangolin_designation="JN.1.1",
            who_label="Variant of Interest",
            defining_mutations=["S:L455S", "S:F456L"],
            initial_proportion=0.65,
            fitness_advantage=0.09,
        ),
    ]

    res = engine.simulate_phylodynamics(
        pathogen_name="SARS-CoV-2",
        seeds=seeds,
        total_days=60,
        baseline_r0=3.0,
    )

    assert res.pathogen_name == "SARS-CoV-2"
    assert res.total_genomes_analyzed == 125000
    assert len(res.lineages) == 2
    assert len(res.epidemiological_trajectories) >= 4
    assert len(res.phylogenetic_tree_nodes) == 3
    assert res.effective_reproduction_number_rt > 0.5
    assert len(res.recommendations) > 0
