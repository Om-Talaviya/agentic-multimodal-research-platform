"""Tests for Phase 269: Autonomous Intact-Glycoprotein Top-Down Tandem Mass Spectrometry (MS/MS) Site-Specific Microheterogeneity Resolver Engine."""

import pytest
from research.orchestration.intact_glycoproteomics_top_down_ms_engine import IntactGlycoproteomicsTopDownMsEngine


def test_intact_glycoproteomics_top_down_ms_engine():
    engine = IntactGlycoproteomicsTopDownMsEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="intact-glycoproteomics-top-down-ms",
        input_scale=1.0,
    )
    assert getattr(result, "glycoform_site_occupancy_resolution_score") != 0
    assert getattr(result, "intact_mass_error_ppm") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
