"""Tests for Phase 364: Autonomous Microbiome-Gut-Brain Axis Metabolite Signaling & Neuroactive Neurotransmitter Modeler Repo."""

import pytest
from database.repositories.gut_brain_axis_metabolome_repo import GutBrainAxisMetabolomeRepository


@pytest.mark.asyncio
async def test_gut_brain_axis_metabolome_repository(db_session):
    repo = GutBrainAxisMetabolomeRepository(db_session)

    study = await repo.create_study(
        name="Study_364_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="gut-brain-axis-metabolome",
        neuroactive_metabolite_synthesis_rate_umol_hr=34.5,
        blood_brain_barrier_integrity_enhancement_fold=1.95,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 364 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_364_Verification"
    assert getattr(study, "neuroactive_metabolite_synthesis_rate_umol_hr") == 34.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Microbial_Tryptophan_Indole_Metabolite_Neuroprotection_Mesh",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Microbial_Tryptophan_Indole_Metabolite_Neuroprotection_Mesh"

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
    assert fetched.name == "Study_364_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
