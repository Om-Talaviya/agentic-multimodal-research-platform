"""Tests for Phase 376: Autonomous Riboswitch-Targeting RNA Small-Molecule Kinetic Binding & Conformation Assayer Repo."""

import pytest
from database.repositories.riboswitch_rna_ligand_binding_repo import RiboswitchRnaLigandBindingRepository


@pytest.mark.asyncio
async def test_riboswitch_rna_ligand_binding_repository(db_session):
    repo = RiboswitchRnaLigandBindingRepository(db_session)

    study = await repo.create_study(
        name="Study_376_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="riboswitch-rna-ligand-binding",
        rna_small_molecule_binding_affinity_apparent_kd_nm=14.5,
        transcriptional_attenuation_dynamic_range_fold=35.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 376 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_376_Verification"
    assert getattr(study, "rna_small_molecule_binding_affinity_apparent_kd_nm") == 14.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Guanine_Riboswitch_Aptamer_Small_Molecule_Docking_Screen",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Guanine_Riboswitch_Aptamer_Small_Molecule_Docking_Screen"

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
    assert fetched.name == "Study_376_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
