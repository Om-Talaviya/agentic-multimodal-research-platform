"""Tests for Phase 314: Autonomous Multi-Strain Synthetic Microbial Consortia Metabolic Cross-Feeding & Syntrophy Balancer Repo."""

import pytest
from database.repositories.microbial_consortia_syntrophy_repo import MicrobialConsortiaSyntrophyRepository


@pytest.mark.asyncio
async def test_microbial_consortia_syntrophy_repository(db_session):
    repo = MicrobialConsortiaSyntrophyRepository(db_session)

    study = await repo.create_study(
        name="Study_314_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="microbial-consortia-syntrophy",
        consortium_steady_state_stability_hours=720.0,
        metabolic_conversion_yield_pct=91.8,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 314 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_314_Verification"
    assert getattr(study, "consortium_steady_state_stability_hours") == 720.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Tri_Species_Cellulose_to_Biobutanol_Syntrophic_Consortium",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Tri_Species_Cellulose_to_Biobutanol_Syntrophic_Consortium"

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
    assert fetched.name == "Study_314_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
