"""Tests for Phase 253: Autonomous Single-Molecule FISH Subcellular RNA Transcript Localization & Cluster Analysis Engine Repo."""

import pytest
from database.repositories.smfish_subcellular_rna_localization_repo import SmfishSubcellularRnaLocalizationRepository


@pytest.mark.asyncio
async def test_smfish_subcellular_rna_localization_repository(db_session):
    repo = SmfishSubcellularRnaLocalizationRepository(db_session)

    study = await repo.create_study(
        name="Study_253_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="smfish-subcellular-rna-localization",
        psf_localization_precision_nm=12.4,
        subcellular_clustering_ripleys_k_score=3.6,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 253 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_253_Verification"
    assert getattr(study, "psf_localization_precision_nm") == 12.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Beta_Actin_3UTR_Perinuclear_Localization_Profile",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Beta_Actin_3UTR_Perinuclear_Localization_Profile"

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
    assert fetched.name == "Study_253_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
