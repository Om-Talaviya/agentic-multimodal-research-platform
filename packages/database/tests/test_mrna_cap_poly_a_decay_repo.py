"""Tests for Phase 219: Autonomous Synthetic mRNA 5' Cap Structure & Poly(A) Tail Deadenylation Decay Kinetics Simulator Engine Repo."""

import pytest
from database.repositories.mrna_cap_poly_a_decay_repo import MrnaCapPolyADecayRepository


@pytest.mark.asyncio
async def test_mrna_cap_poly_a_decay_repository(db_session):
    repo = MrnaCapPolyADecayRepository(db_session)

    study = await repo.create_study(
        name="Study_219_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="mrna-cap-poly-a-decay",
        mrna_half_life_hours=38.6,
        initiation_complex_affinity_kd_nM=14.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 219 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_219_Verification"
    assert getattr(study, "mrna_half_life_hours") == 38.6

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Cap1_PolyA120_ModRNA_Luciferase_Construct",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Cap1_PolyA120_ModRNA_Luciferase_Construct"

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
    assert fetched.name == "Study_219_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
