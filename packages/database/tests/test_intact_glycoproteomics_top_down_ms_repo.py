"""Tests for Phase 269: Autonomous Intact-Glycoprotein Top-Down Tandem Mass Spectrometry (MS/MS) Site-Specific Microheterogeneity Resolver Repo."""

import pytest
from database.repositories.intact_glycoproteomics_top_down_ms_repo import IntactGlycoproteomicsTopDownMsRepository


@pytest.mark.asyncio
async def test_intact_glycoproteomics_top_down_ms_repository(db_session):
    repo = IntactGlycoproteomicsTopDownMsRepository(db_session)

    study = await repo.create_study(
        name="Study_269_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="intact-glycoproteomics-top-down-ms",
        glycoform_site_occupancy_resolution_score=98.2,
        intact_mass_error_ppm=1.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 269 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_269_Verification"
    assert getattr(study, "glycoform_site_occupancy_resolution_score") == 98.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Therapeutic_Epoetin_Intact_Glycoform_Deconvolution",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Therapeutic_Epoetin_Intact_Glycoform_Deconvolution"

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
    assert fetched.name == "Study_269_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
