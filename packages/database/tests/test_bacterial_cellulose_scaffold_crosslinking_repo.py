"""Tests for Phase 462: Autonomous Living Biomaterial Engineered Bacterial Cellulose Scaffold Cross-Linking Engine Repo."""

import pytest
from database.repositories.bacterial_cellulose_scaffold_crosslinking_repo import BacterialCelluloseScaffoldRepository


@pytest.mark.asyncio
async def test_bacterial_cellulose_scaffold_crosslinking_repository(db_session):
    repo = BacterialCelluloseScaffoldRepository(db_session)

    study = await repo.create_study(
        name="Study_462_Verification",
        target_specimen="Komagataeibacter xylinus Pellicle Hydrogel with Genetically Encoded SpyTag/SpyCatcher Nodes",
        analytical_modality="living-bacterial-cellulose",
        youngs_elastic_modulus_megapascals=42.5,
        microfibril_crystallinity_index=0.865,
        tensile_fracture_toughness_kj_per_m2=18.4,
        water_retention_swelling_ratio=14.2,
        confidence_score=0.988,
        status="completed",
        summary_report="Phase 462 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_462_Verification"
    assert study.youngs_elastic_modulus_megapascals == 42.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Isopeptide_SpyTag_Catcher_Polymer_Crosslink",
        profile_category="Primary Step",
        quantitative_value=42.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Isopeptide_SpyTag_Catcher_Polymer_Crosslink"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="youngs_elastic_modulus_megapascals",
        observed_value=42.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 42.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_462_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
