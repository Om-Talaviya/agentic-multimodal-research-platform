"""Tests for Phase 272: Autonomous High-Throughput Chemoproteomics Activity-Based Protein Profiling (ABPP) Covalent Ligand Screen Repo."""

import pytest
from database.repositories.chemoproteomics_abpp_covalent_screen_repo import ChemoproteomicsAbppCovalentScreenRepository


@pytest.mark.asyncio
async def test_chemoproteomics_abpp_covalent_screen_repository(db_session):
    repo = ChemoproteomicsAbppCovalentScreenRepository(db_session)

    study = await repo.create_study(
        name="Study_272_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="chemoproteomics-abpp-covalent-screen",
        proteome_wide_covalent_engagement_selectivity=96.4,
        ligandable_cystiene_residue_count=420.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 272 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_272_Verification"
    assert getattr(study, "proteome_wide_covalent_engagement_selectivity") == 96.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Cysteine_Reactive_Acrylamide_Probe_Proteome_Map",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Cysteine_Reactive_Acrylamide_Probe_Proteome_Map"

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
    assert fetched.name == "Study_272_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
