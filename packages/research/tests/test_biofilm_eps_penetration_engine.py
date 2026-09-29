"""Tests for Phase 357: Autonomous Bacterial Biofilm Extracellular Polymeric Substance (EPS) Disruption & Penetration Simulator Engine."""

import pytest
from research.orchestration.biofilm_eps_penetration_engine import BiofilmEpsPenetrationEngine


def test_biofilm_eps_penetration_engine():
    engine = BiofilmEpsPenetrationEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="biofilm-eps-penetration",
        input_scale=1.0,
    )
    assert getattr(result, "biofilm_biomass_eradication_efficiency_pct") != 0
    assert getattr(result, "antimicrobial_diffusive_penetration_rate_um_min") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
