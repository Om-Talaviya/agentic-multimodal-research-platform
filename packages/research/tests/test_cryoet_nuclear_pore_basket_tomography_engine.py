"""Tests for Phase 438: Autonomous Cryo-ET In-Situ Nuclear Pore Complex (NPC) Nuclear Basket Dynamic Conformation Engine."""

import pytest
from research.orchestration.cryoet_nuclear_pore_basket_tomography_engine import CryoetNuclearPoreBasketEngine


def test_cryoet_nuclear_pore_basket_tomography_engine():
    engine = CryoetNuclearPoreBasketEngine()
    result = engine.analyze(
        target_specimen="Intact HeLa Cell Nuclear Envelope Vitreous Lamella with 8-Fold NPC Basket",
        analytical_modality="cryoet-npc-basket",
        input_scale=1.0,
    )

    assert result.target_specimen == "Intact HeLa Cell Nuclear Envelope Vitreous Lamella with 8-Fold NPC Basket"
    assert result.confidence_score >= 0.95
    assert result.subtomogram_average_resolution_angstrom > 0.0
    assert result.basket_dilation_radius_nm > 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Cryo-ET In-Situ Nuc" in result.summary_report
