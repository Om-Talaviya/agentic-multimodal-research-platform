"""Tests for Phase 536: Autonomous In-Situ Cryo-ET Endoplasmic Reticulum-Mitochondria Membrane Curvature Elastic Stress Profiler."""

import pytest
from research.orchestration.cryoet_organelle_membrane_curvature_stress_engine import CryoetOrganelleMembraneCurvatureStressEngine


def test_cryoet_organelle_membrane_curvature_stress_engine():
    engine = CryoetOrganelleMembraneCurvatureStressEngine()
    result = engine.analyze(
        target_specimen="Vitrified Primary Murine Hepatocyte Lamella showing In-Situ MAM (Mitochondria-Associated ER Membrane) Junctions",
        analytical_modality="cryoet-organelle-membrane-stress",
        input_scale=1.0,
    )

    assert result.target_specimen == "Vitrified Primary Murine Hepatocyte Lamella showing In-Situ MAM (Mitochondria-Associated ER Membrane) Junctions"
    assert result.confidence_score >= 0.95
    assert result.membrane_bending_modulus_kbT != 0.0
    assert result.mam_intermembrane_contact_distance_nm != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous In-Situ Cryo-ET End" in result.summary_report
