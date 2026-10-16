"""Tests for Phase 561: Autonomous High-Throughput Deep Ocean Hydrothermal Vent Metagenomic Novel Enzyme Prospector Repo."""

import pytest
from database.repositories.ocean_hydrothermal_metagenomic_enzyme_prospector_repo import OceanHydrothermalMetagenomicEnzymeProspectorRepository


@pytest.mark.asyncio
async def test_ocean_hydrothermal_metagenomic_enzyme_prospector_repository(db_session):
    repo = OceanHydrothermalMetagenomicEnzymeProspectorRepository(db_session)

    study = await repo.create_study(
        name="Study_561_Verification",
        target_specimen="Deep-Sea Metagenomic DNA from Mid-Atlantic Ridge Black Smoker Vent Hydrothermal Fluid at 320C and 300 Bar",
        analytical_modality="deep-sea-metagenomic-biocatalysis",
        thermostable_extremozyme_catalytic_half_life_hours=72.0,
        novel_biocatalytic_family_discovery_count=34.0,
        piezophilic_activation_volume_delta_v_ml_mol=-28.5,
        optimum_catalytic_temperature_celsius=108.5,
        confidence_score=0.995,
        status="completed",
        summary_report="Phase 561 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_561_Verification"
    assert study.thermostable_extremozyme_catalytic_half_life_hours == 72.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Hyperthermophilic_Esterase_Catalytic_Triad_Fold",
        profile_category="Primary Step",
        quantitative_value=72.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Hyperthermophilic_Esterase_Catalytic_Triad_Fold"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="thermostable_extremozyme_catalytic_half_life_hours",
        observed_value=72.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 72.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_561_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
