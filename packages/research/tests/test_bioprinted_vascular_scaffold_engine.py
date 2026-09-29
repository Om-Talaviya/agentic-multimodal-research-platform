"""Tests for Phase 366: Autonomous 3D Bioprinted Vascularized Tissue Scaffold Fluid Shear & Endothelial Sprouting Simulator Engine."""

import pytest
from research.orchestration.bioprinted_vascular_scaffold_engine import BioprintedVascularScaffoldEngine


def test_bioprinted_vascular_scaffold_engine():
    engine = BioprintedVascularScaffoldEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="bioprinted-vascular-scaffold",
        input_scale=1.0,
    )
    assert getattr(result, "capillary_network_perfusion_flow_rate_ul_min") != 0
    assert getattr(result, "endothelial_lumen_patency_fraction_pct") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
