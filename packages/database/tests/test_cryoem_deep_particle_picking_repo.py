"""Tests for Phase 275: Autonomous Deep Learning Cryo-EM Raw Micrograph Particle Picking & Ice Contamination Filter Repo."""

import pytest
from database.repositories.cryoem_deep_particle_picking_repo import CryoemDeepParticlePickingRepository


@pytest.mark.asyncio
async def test_cryoem_deep_particle_picking_repository(db_session):
    repo = CryoemDeepParticlePickingRepository(db_session)

    study = await repo.create_study(
        name="Study_275_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="cryoem-deep-particle-picking",
        particle_picking_precision_f1_score=96.8,
        ice_contamination_rejection_rate_pct=99.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 275 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_275_Verification"
    assert getattr(study, "particle_picking_precision_f1_score") == 96.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Apoferritin_High_Contrast_Cryo_Particle_Pick",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Apoferritin_High_Contrast_Cryo_Particle_Pick"

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
    assert fetched.name == "Study_275_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
