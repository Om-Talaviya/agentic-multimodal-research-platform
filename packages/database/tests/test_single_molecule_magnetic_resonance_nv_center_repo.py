"""Tests for Phase 436: Autonomous Diamond NV-Center Nanoscale Single-Molecule Magnetic Resonance Engine Repo."""

import pytest
from database.repositories.single_molecule_magnetic_resonance_nv_center_repo import SingleMoleculeNvCenterNmrRepository


@pytest.mark.asyncio
async def test_single_molecule_magnetic_resonance_nv_center_repository(db_session):
    repo = SingleMoleculeNvCenterNmrRepository(db_session)

    study = await repo.create_study(
        name="Study_436_Verification",
        target_specimen="Diamond Nitrogen-Vacancy (NV) Center Nanocrystal with Surface Immobilized Ferritin",
        analytical_modality="nv-center-nanoscale-nmr",
        spin_coherence_time_t2_us=145.0,
        magnetic_sensitivity_nT_per_sqrthz=2.45,
        optically_detected_mr_dip_contrast=0.185,
        spatial_standoff_distance_nm=3.2,
        confidence_score=0.992,
        status="completed",
        summary_report="Phase 436 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_436_Verification"
    assert study.spin_coherence_time_t2_us == 145.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="ODMR_Zeeman_Splitting_Peak",
        profile_category="Primary Step",
        quantitative_value=145.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "ODMR_Zeeman_Splitting_Peak"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="spin_coherence_time_t2_us",
        observed_value=145.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 145.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_436_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
