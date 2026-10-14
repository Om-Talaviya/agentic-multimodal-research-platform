"""Tests for Phase 475: Autonomous Multiplexed Bio-Acoustic Cellular Impedance Flow Cytometry Classifier Repo."""

import pytest
from database.repositories.acoustic_impedance_cytometry_repo import AcousticImpedanceCytometryRepository


@pytest.mark.asyncio
async def test_acoustic_impedance_cytometry_repository(db_session):
    repo = AcousticImpedanceCytometryRepository(db_session)

    study = await repo.create_study(
        name="Study_475_Verification",
        target_specimen="High-Throughput Microfluidic Coplanar Electrode Microchannel with Circulating Tumor Cell Suspensions",
        analytical_modality="acoustic-impedance-cytometry",
        dielectric_membrane_capacitance_uF_per_cm2=1.25,
        cytoplasm_conductivity_S_per_m=0.68,
        acoustic_focusing_transit_time_uniformity_cv=0.032,
        single_cell_classification_accuracy=0.985,
        confidence_score=0.992,
        status="completed",
        summary_report="Phase 475 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_475_Verification"
    assert study.dielectric_membrane_capacitance_uF_per_cm2 == 1.25

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Multifrequency_Impedance_Opacity_Deconvolution",
        profile_category="Primary Step",
        quantitative_value=1.25,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Multifrequency_Impedance_Opacity_Deconvolution"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="dielectric_membrane_capacitance_uF_per_cm2",
        observed_value=1.25,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 1.25

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_475_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
