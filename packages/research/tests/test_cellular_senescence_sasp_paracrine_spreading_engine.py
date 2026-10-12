"""Tests for Phase 443: Autonomous Cellular Senescence-Associated Secretory Phenotype (SASP) Paracrine Spreading & Tissue Exhaustion Engine."""

import pytest
from research.orchestration.cellular_senescence_sasp_paracrine_spreading_engine import CellularSenescenceSaspEngine


def test_cellular_senescence_sasp_paracrine_spreading_engine():
    engine = CellularSenescenceSaspEngine()
    result = engine.analyze(
        target_specimen="Replicative Senescent Human Dermal Fibroblasts in 3D Collagen Microtissue with Bystander Cells",
        analytical_modality="senescence-sasp-spreading",
        input_scale=1.0,
    )

    assert result.target_specimen == "Replicative Senescent Human Dermal Fibroblasts in 3D Collagen Microtissue with Bystander Cells"
    assert result.confidence_score >= 0.95
    assert result.sasp_paracrine_diffusion_radius_um > 0.0
    assert result.p16_ink4a_induction_fold_change > 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Cellular Senescence" in result.summary_report
