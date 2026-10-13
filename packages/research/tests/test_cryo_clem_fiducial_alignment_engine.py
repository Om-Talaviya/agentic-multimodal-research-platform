"""Tests for Phase 460: Autonomous In-Situ Cryo-CLEM Fluorescent Target Correlation & Precision Fiducial Alignment Engine."""

import pytest
from research.orchestration.cryo_clem_fiducial_alignment_engine import CryoClemFiducialAlignmentEngine


def test_cryo_clem_fiducial_alignment_engine():
    engine = CryoClemFiducialAlignmentEngine()
    result = engine.analyze(
        target_specimen="Vitrified Primary Axon Growth Cone with Gold Nanoparticle Fiducials and GFP-Tagged Cargo",
        analytical_modality="cryo-clem-fiducial-alignment",
        input_scale=1.0,
    )

    assert result.target_specimen == "Vitrified Primary Axon Growth Cone with Gold Nanoparticle Fiducials and GFP-Tagged Cargo"
    assert result.confidence_score >= 0.95
    assert result.coordinate_transformation_target_registration_error_nm != 0.0
    assert result.fiducial_triangulation_residual_angstrom != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous In-Situ Cryo-CLEM F" in result.summary_report
