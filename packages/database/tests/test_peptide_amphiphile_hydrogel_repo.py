"""Tests for Phase 369: Autonomous Self-Assembling Peptide Amphiphile Supramolecular Hydrogel Nanofiber Matrix Modeler Repo."""

import pytest
from database.repositories.peptide_amphiphile_hydrogel_repo import PeptideAmphiphileHydrogelRepository


@pytest.mark.asyncio
async def test_peptide_amphiphile_hydrogel_repository(db_session):
    repo = PeptideAmphiphileHydrogelRepository(db_session)

    study = await repo.create_study(
        name="Study_369_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="peptide-amphiphile-hydrogel",
        nanofiber_youngs_modulus_elastic_storage_g_prime_pa=1850.0,
        neurite_outgrowth_extension_rate_um_day=145.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 369 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_369_Verification"
    assert getattr(study, "nanofiber_youngs_modulus_elastic_storage_g_prime_pa") == 1850.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Neural_Regenerative_IKVAV_Peptide_Amphiphile_Nanofiber",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Neural_Regenerative_IKVAV_Peptide_Amphiphile_Nanofiber"

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
    assert fetched.name == "Study_369_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
