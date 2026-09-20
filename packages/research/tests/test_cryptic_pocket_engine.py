"""
Unit tests for Phase 107: Allosteric Pocket Discovery & Cryptic Binding Site Engine.
"""
import pytest
from research.structural.cryptic_pocket_engine import CrypticPocketEngine

def test_druggability_calculation():
    engine = CrypticPocketEngine()
    
    # Large hydrophobic pocket -> High druggability >= 0.70
    score_high = engine.compute_druggability_index(volume_a3=600.0, hydrophobicity=0.85)
    assert score_high >= 0.70

    # Very small hydrophilic cavity -> Low druggability <= 0.30
    score_low = engine.compute_druggability_index(volume_a3=80.0, hydrophobicity=0.20)
    assert score_low <= 0.30

def test_cryptic_discovery_workflow():
    engine = CrypticPocketEngine()
    
    discovery = engine.discover_cryptic_pockets(
        target_protein="KRAS-G12D",
        pdb_id="7T47",
        trajectory_frames_sampled=150
    )

    assert discovery["target_protein"] == "KRAS-G12D"
    assert discovery["detected_cryptic_pockets"] == 3
    assert discovery["max_druggability_score"] > 0.70
    assert len(discovery["coupled_networks"]) == 3
    assert discovery["allosteric_coupling_score"] > 0.60
