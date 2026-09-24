"""Tests for TCellEngagerGeometryEngine (Phase 158)."""

from research.immunology.tcell_engager_geometry_engine import (
    TCellEngagerGeometryEngine,
    TCellEngagerRequest,
)


def test_tcell_engager_geometry_engine():
    engine = TCellEngagerGeometryEngine()
    req = TCellEngagerRequest(
        construct_name="CD19 x CD20 x CD3e TriTE",
        modality_format="TriTE",
        primary_tumor_antigen="B-Cell Lymphoma Dual-Target",
        cd3_arm_affinity_nM=15.0,
    )
    result = engine.model_synapse_geometry(req)
    assert result.cytolytic_potency_ec50_pm > 0
    assert result.synaptic_cleft_distance_a > 50.0
    assert len(result.binding_domains) == 3
    assert len(result.synapse_profiles) == 3
