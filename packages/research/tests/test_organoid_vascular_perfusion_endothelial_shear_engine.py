"""Tests for Phase 510: Autonomous Vascularized Cerebral Organoid Lumen Shear Stress & Perfusion Simulator."""

import pytest
from research.orchestration.organoid_vascular_perfusion_endothelial_shear_engine import OrganoidVascularPerfusionEndothelialShearEngine


def test_organoid_vascular_perfusion_endothelial_shear_engine():
    engine = OrganoidVascularPerfusionEndothelialShearEngine()
    result = engine.analyze(
        target_specimen="3D Bioprinted Endothelialized Hydrogel Microchannel Lattice Interfaced with Cortical Brain Organoids",
        analytical_modality="organoid-microvascular-perfusion",
        input_scale=1.0,
    )

    assert result.target_specimen == "3D Bioprinted Endothelialized Hydrogel Microchannel Lattice Interfaced with Cortical Brain Organoids"
    assert result.confidence_score >= 0.95
    assert result.microvascular_lumen_wall_shear_stress_pa != 0.0
    assert result.interstitial_oxygen_partial_pressure_mmHg != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Vascularized Cerebr" in result.summary_report
