"""Tests for Phase 290: Autonomous Intact Membrane Protein Native Mass Spectrometry & Lipid-Binding Stoichiometry Engine Repo."""

import pytest
from database.repositories.native_mass_spec_membrane_protein_repo import NativeMassSpecMembraneProteinRepository


@pytest.mark.asyncio
async def test_native_mass_spec_membrane_protein_repository(db_session):
    repo = NativeMassSpecMembraneProteinRepository(db_session)

    study = await repo.create_study(
        name="Study_290_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="native-mass-spec-membrane-protein",
        oligomeric_stoichiometry_confidence_score=99.1,
        lipid_dissociation_constant_kd_uM=3.4,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 290 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_290_Verification"
    assert getattr(study, "oligomeric_stoichiometry_confidence_score") == 99.1

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Kv1_2_Potassium_Channel_Phospholipid_Binding_Profile",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Kv1_2_Potassium_Channel_Phospholipid_Binding_Profile"

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
    assert fetched.name == "Study_290_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
