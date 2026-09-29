"""Tests for Phase 349: Autonomous Therapeutic Oligonucleotide Chemical Modification (PS/2-MOE/LNA) Stability & Affinity Optimizer Repo."""

import pytest
from database.repositories.oligo_chem_modifier_optimizer_repo import OligoChemModifierOptimizerRepository


@pytest.mark.asyncio
async def test_oligo_chem_modifier_optimizer_repository(db_session):
    repo = OligoChemModifierOptimizerRepository(db_session)

    study = await repo.create_study(
        name="Study_349_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="oligo-chem-modifier",
        duplex_thermal_stability_delta_tm_per_mod_celsius=3.6,
        serum_exonuclease_resistance_half_life_hr=96.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 349 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_349_Verification"
    assert getattr(study, "duplex_thermal_stability_delta_tm_per_mod_celsius") == 3.6

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Stereopure_PS_2_MOE_Antisense_Gapmer_Huntingtin_Silencer",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Stereopure_PS_2_MOE_Antisense_Gapmer_Huntingtin_Silencer"

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
    assert fetched.name == "Study_349_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
