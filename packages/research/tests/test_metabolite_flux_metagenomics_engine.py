"""Tests for Phase 225: Autonomous Metagenomic Metabolic Flux & Gut-Liver Axis Co-Metabolism Simulator Engine Engine."""

import pytest
from research.orchestration.metabolite_flux_metagenomics_engine import MetaboliteFluxMetagenomicsEngine


def test_metabolite_flux_metagenomics_engine():
    engine = MetaboliteFluxMetagenomicsEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="metabolite-flux-metagenomics",
        input_scale=1.0,
    )
    assert getattr(result, "scfa_butyrate_production_mmol_gDW_h") != 0
    assert getattr(result, "microbiome_host_flux_coupling_index") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
