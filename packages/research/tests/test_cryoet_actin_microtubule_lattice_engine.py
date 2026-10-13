"""Tests for Phase 469: Autonomous In-Situ Cryo-ET Cytoskeletal Actin-Microtubule Cross-Linking Structural Lattice Engine."""

import pytest
from research.orchestration.cryoet_actin_microtubule_lattice_engine import CryoetActinMicrotubuleLatticeEngine


def test_cryoet_actin_microtubule_lattice_engine():
    engine = CryoetActinMicrotubuleLatticeEngine()
    result = engine.analyze(
        target_specimen="Vitrified Primary Growth Cone Cytoskeleton with Septin/Plectin Cross-Linked Filament Assemblies",
        analytical_modality="cryoet-actin-microtubule-lattice",
        input_scale=1.0,
    )

    assert result.target_specimen == "Vitrified Primary Growth Cone Cytoskeleton with Septin/Plectin Cross-Linked Filament Assemblies"
    assert result.confidence_score >= 0.95
    assert result.crosslinker_bridge_density_per_um != 0.0
    assert result.filament_intersection_angle_distribution_deg != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous In-Situ Cryo-ET Cyt" in result.summary_report
