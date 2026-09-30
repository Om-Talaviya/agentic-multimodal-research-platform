"""Tests for Phase 381: Autonomous Single-Cell DNA Methylation and Hydroxymethylation (5mC/5hmC) Bisulfite-Free Caller Engine."""

import pytest
from research.orchestration.singlecell_5mc_5hmc_caller_engine import Singlecell5mc5hmcCallerEngine


def test_singlecell_5mc_5hmc_caller_engine():
    engine = Singlecell5mc5hmcCallerEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="singlecell-5mc-5hmc-caller",
        input_scale=1.0,
    )
    assert getattr(result, "base_resolution_5hmc_calling_precision_pct") != 0
    assert getattr(result, "single_cell_cpg_site_coverage_depth_fold") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
