"""Tests for Phase 398: High-Resolution Icosahedral Viral Capsid Cryo-EM Symmetry Reconstructor Engine."""

import pytest
from research.orchestration.viral_capsid_cryoem_reconstructor_engine import ViralCapsidCryoemReconstructorEngine


def test_viral_capsid_cryoem_reconstructor_engine():
    engine = ViralCapsidCryoemReconstructorEngine()
    result = engine.analyze(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="viral-capsid-cryoem-reconstruction",
        input_scale=1.0,
    )

    assert result.target_specimen == "Human Patient Cohort Sample"
    assert result.confidence_score >= 0.95
    assert getattr(result, "reconstructed_cryo_em_map_fsc_resolution_angstrom") > 0
    assert getattr(result, "icosahedral_symmetry_alignment_angular_precision_deg") > 0
    assert len(result.item_profiles) == 3
    assert len(result.metric_traces) == 3
    assert "Phase 398" in result.summary_report
