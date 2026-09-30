"""Tests for Phase 403: Autonomous Injectable Supramolecular Peptide Shear-Thinning Biomaterial Modeler Repo."""

import pytest
from database.repositories.supramolecular_peptide_hydrogel_repo import SupramolecularPeptideHydrogelRepository


@pytest.mark.asyncio
async def test_supramolecular_peptide_hydrogel_repository(db_session):
    repo = SupramolecularPeptideHydrogelRepository(db_session)

    study = await repo.create_study(
        name="Study_403_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="supramolecular-peptide-hydrogel",
        storage_modulus_g_prime_plateau_pascals=3450.0,
        shear_thinning_recovery_half_time_seconds=1.45,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 403 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_403_Verification"
    assert getattr(study, "storage_modulus_g_prime_plateau_pascals") == 3450.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Fmoc_FF_Diphenylalanine_Self_Assembling_Nanofiber_Matrix",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Fmoc_FF_Diphenylalanine_Self_Assembling_Nanofiber_Matrix"

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
    assert fetched.name == "Study_403_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
