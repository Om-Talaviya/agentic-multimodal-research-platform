"""Tests for Phase 435: Autonomous Reconfigurable DNA Origami Dynamic Hinge Compliant Nano-Actuator Engine Repo."""

import pytest
from database.repositories.dna_origami_dynamic_hinge_biosensor_repo import DnaOrigamiDynamicHingeRepository


@pytest.mark.asyncio
async def test_dna_origami_dynamic_hinge_biosensor_repository(db_session):
    repo = DnaOrigamiDynamicHingeRepository(db_session)

    study = await repo.create_study(
        name="Study_435_Verification",
        target_specimen="Hexagonal Bundle DNA Origami Nano-Hinge with Fluorophore/Quencher FRET Pair",
        analytical_modality="dna-origami-hinge",
        hinge_flexibility_angle_deg=62.4,
        fret_efficiency_dynamic_ratio=0.865,
        folding_yield_percentage=91.2,
        magnesium_stabilization_mM=12.5,
        confidence_score=0.988,
        status="completed",
        summary_report="Phase 435 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_435_Verification"
    assert study.hinge_flexibility_angle_deg == 62.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Origami_Scaffold_Hinge_Angular_Transition",
        profile_category="Primary Step",
        quantitative_value=62.4,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Origami_Scaffold_Hinge_Angular_Transition"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="hinge_flexibility_angle_deg",
        observed_value=62.4,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 62.4

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_435_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
