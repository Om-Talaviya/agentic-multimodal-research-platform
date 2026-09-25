"""Tests for Phase 184: Fragment-Based Lead Discovery Engine."""

import pytest
from research.chemistry.fragment_based_lead_discovery_engine import FBDDLeadDiscoveryEngine


def test_fragment_based_lead_discovery_simulation():
    engine = FBDDLeadDiscoveryEngine()
    result = engine.simulate_fbdd_pipeline(
        target_protein_pocket="KRAS-G12D Switch-II Pocket",
        fragment_library_size=1500,
        linker_growth_strategy="fragment_linking_rigid",
        target_subpockets_count=2,
    )

    assert result.target_protein_pocket == "KRAS-G12D Switch-II Pocket"
    assert result.mean_ligand_efficiency >= 0.30
    assert len(result.fragment_hits) == 3
    assert len(result.linker_candidates) == 2
    assert result.optimized_lead_predicted_pic50 > 7.0
    assert result.lead_optimization_index > 0.0