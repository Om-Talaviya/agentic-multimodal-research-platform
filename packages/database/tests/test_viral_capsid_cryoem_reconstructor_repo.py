"""Tests for Phase 398: High-Resolution Icosahedral Viral Capsid Cryo-EM Symmetry Reconstructor Repo."""

import pytest
from database.repositories.viral_capsid_cryoem_reconstructor_repo import ViralCapsidCryoemReconstructorRepository


@pytest.mark.asyncio
async def test_viral_capsid_cryoem_reconstructor_repository(db_session):
    repo = ViralCapsidCryoemReconstructorRepository(db_session)

    study = await repo.create_study(
        name="Study_398_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="viral-capsid-cryoem-reconstruction",
        reconstructed_cryo_em_map_fsc_resolution_angstrom=1.85,
        icosahedral_symmetry_alignment_angular_precision_deg=0.12,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 398 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_398_Verification"
    assert getattr(study, "reconstructed_cryo_em_map_fsc_resolution_angstrom") == 1.85

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="AAV9_Full_Capsid_Subunit_VP3_Pore_Assembly_Model",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "AAV9_Full_Capsid_Subunit_VP3_Pore_Assembly_Model"

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
    assert fetched.name == "Study_398_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
