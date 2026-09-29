"""Tests for Phase 337: Autonomous High-Dimensional Cytometry (Mass/Spectral CyTOF) Immune Cell Phenotype Clustering Engine Repo."""

import pytest
from database.repositories.cytof_mass_cytometry_clustering_repo import CytofMassCytometryClusteringRepository


@pytest.mark.asyncio
async def test_cytof_mass_cytometry_clustering_repository(db_session):
    repo = CytofMassCytometryClusteringRepository(db_session)

    study = await repo.create_study(
        name="Study_337_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="cytof-mass-cytometry",
        immune_subpopulation_silhouette_score=0.88,
        isotopic_channel_crosstalk_attenuation_pct=99.1,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 337 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_337_Verification"
    assert getattr(study, "immune_subpopulation_silhouette_score") == 0.88

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="CAR_T_Exhaustion_60_Marker_Spectral_CyTOF_Panel",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "CAR_T_Exhaustion_60_Marker_Spectral_CyTOF_Panel"

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
    assert fetched.name == "Study_337_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
