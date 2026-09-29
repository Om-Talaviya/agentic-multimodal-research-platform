"""Tests for Phase 293: Autonomous Non-Viral Lipid Nanoparticle (LNP) Endosomal Escape Kinetics & Bioavailability Forecaster Engine."""

import pytest
from research.orchestration.lnp_endosomal_escape_kinetics_engine import LnpEndosomalEscapeKineticsEngine


def test_lnp_endosomal_escape_kinetics_engine():
    engine = LnpEndosomalEscapeKineticsEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="lnp-endosomal-escape-kinetics",
        input_scale=1.0,
    )
    assert getattr(result, "cytosolic_payload_escape_efficiency_pct") != 0
    assert getattr(result, "endosomal_rupture_half_time_minutes") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
