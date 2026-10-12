"""Tests for Phase 429: Autonomous Whole-Cell Organelle Contact Site & Membrane Proximity Distance Transformer."""

import pytest
from research.orchestration.organelle_contact_site_proximity_engine import OrganelleContactSiteProximityEngine


def test_organelle_contact_site_proximity_engine():
    engine = OrganelleContactSiteProximityEngine()
    result = engine.analyze(
        target_specimen="Focused Ion Beam Scanning Electron Microscopy (FIB-SEM) Whole Cell",
        analytical_modality="organelle-contact-site",
        input_scale=1.0,
    )

    assert result.target_specimen == "Focused Ion Beam Scanning Electron Microscopy (FIB-SEM) Whole Cell"
    assert result.confidence_score >= 0.95
    assert result.er_mitochondria_contact_distance_nm > 0.0
    assert result.contact_site_surface_area_um2 > 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Whole-Cell Organell" in result.summary_report
