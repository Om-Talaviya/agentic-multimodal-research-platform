"""Tests for Phase 207: Proteome-Wide Ubiquitination & E3 Ligase Selectivity Engine Repo."""

import pytest
from database.repositories.ubiquitination_e3_selectivity_repo import UbiquitinationE3SelectivityRepository


@pytest.mark.asyncio
async def test_ubiquitination_e3_selectivity_repository(db_session):
    repo = UbiquitinationE3SelectivityRepository(db_session)

    study = await repo.create_study(
        name="Study_207_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Ubiquitination E3 Selectivity",
        ubiquitination_site_prediction_auroc=0.948,
        e3_ligase_selectivity_binding_affinity_kd_nm=24.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 207 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_207_Verification"
    assert getattr(study, "ubiquitination_site_prediction_auroc") == 0.948

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Substrate Lysine Ubiquitination Site [BRD4 Lys378 - CRBN mediated]",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Substrate Lysine Ubiquitination Site [BRD4 Lys378 - CRBN mediated]"

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
    assert fetched.name == "Study_207_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
