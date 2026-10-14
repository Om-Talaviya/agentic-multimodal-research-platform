"""Tests for Phase 477: Autonomous Nanoscale Cytoskeletal Actin Ring Constriction & Cytokinesis Cleavage Furrow Modeler."""

import pytest
from research.orchestration.actin_ring_cytokinesis_constriction_engine import ActinRingCytokinesisConstrictionEngine


def test_actin_ring_cytokinesis_constriction_engine():
    engine = ActinRingCytokinesisConstrictionEngine()
    result = engine.analyze(
        target_specimen="Vitrified Dividing S. pombe Protoplast Actomyosin Ring Complex with Myosin-II / Formin Cdc12 Clusters",
        analytical_modality="actin-ring-cytokinesis-constriction",
        input_scale=1.0,
    )

    assert result.target_specimen == "Vitrified Dividing S. pombe Protoplast Actomyosin Ring Complex with Myosin-II / Formin Cdc12 Clusters"
    assert result.confidence_score >= 0.95
    assert result.contractile_ring_tension_pN != 0.0
    assert result.furrow_ingression_velocity_nm_per_s != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Nanoscale Cytoskele" in result.summary_report
