"""Tests for Phase 386: Autonomous Supramolecular DNA Origami Nanorobot Targeted Cargo Release Trigger Modeler Repo."""

import pytest
from database.repositories.dna_origami_nanorobot_cargo_repo import DnaOrigamiNanorobotCargoRepository


@pytest.mark.asyncio
async def test_dna_origami_nanorobot_cargo_repository(db_session):
    repo = DnaOrigamiNanorobotCargoRepository(db_session)

    study = await repo.create_study(
        name="Study_386_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="dna-origami-nanorobot-cargo",
        nanorobot_cargo_payload_retention_stability_pct=99.4,
        target_triggered_opening_kinetics_t50_minutes=12.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 386 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_386_Verification"
    assert getattr(study, "nanorobot_cargo_payload_retention_stability_pct") == 99.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Aptamer_Gated_DNA_Origami_Box_Thrombin_Delivery_Nanorobot",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Aptamer_Gated_DNA_Origami_Box_Thrombin_Delivery_Nanorobot"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="Sensitivity & Recovery Rate",
        observed_value=0.984,
        z_score=2.85,
        p_value=0.00012,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.984

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_386_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
