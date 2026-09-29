"""Tests for Phase 352: Autonomous Multiplexed Ion Beam Imaging (MIBI-TOF) Deep Proteomic Spatial TME Deconvolver Engine."""

import pytest
from research.orchestration.mibi_tof_spatial_proteomics_engine import MibiTofSpatialProteomicsEngine


def test_mibi_tof_spatial_proteomics_engine():
    engine = MibiTofSpatialProteomicsEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="mibi-tof-spatial-proteomics",
        input_scale=1.0,
    )
    assert getattr(result, "lateral_spatial_resolution_nanometers") != 0
    assert getattr(result, "isotopic_ion_channel_signal_to_noise_ratio") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
