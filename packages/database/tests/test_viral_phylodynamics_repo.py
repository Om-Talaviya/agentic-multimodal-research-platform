"""Tests for Phase 132 ViralPhylodynamicsRepository."""

import pytest
from database.repositories.viral_phylodynamics_repo import ViralPhylodynamicsRepository


@pytest.mark.asyncio
async def test_viral_phylodynamics_repo_lifecycle(db_session):
    repo = ViralPhylodynamicsRepository(db_session)

    # 1. Create study
    study = await repo.create_study(
        pathogen_name="SARS-CoV-2",
        genome_type="ssRNA(+)",
        geographic_regions=["North America", "Europe", "East Asia"],
        total_genomes_sequenced=120000,
        effective_reproduction_number_rt=1.42,
        transmission_fitness_gain_pct=31.5,
        metadata_json={"sequencing_consortium": "GISAID / Nextstrain"},
    )
    assert study.id is not None
    assert study.pathogen_name == "SARS-CoV-2"
    assert study.total_genomes_sequenced == 120000

    # 2. Add lineages
    lineage1 = await repo.add_lineage(
        study_id=study.id,
        lineage_clade="23I (Omicron)",
        pangolin_designation="BA.2.86",
        who_label="Pirola",
        defining_mutations=["S:K356T", "S:V483del", "S:P681R"],
        growth_advantage_daily=0.065,
        immune_evasion_score=0.82,
        global_prevalence_pct=18.4,
    )
    lineage2 = await repo.add_lineage(
        study_id=study.id,
        lineage_clade="24A (JN.1)",
        pangolin_designation="JN.1.11.1",
        who_label="Variant of Interest",
        defining_mutations=["S:L455S", "S:F456L", "S:R346T"],
        growth_advantage_daily=0.115,
        immune_evasion_score=0.94,
        global_prevalence_pct=58.2,
    )
    assert lineage1.id is not None
    assert lineage2.pangolin_designation == "JN.1.11.1"

    # 3. Add fitness profile
    profile = await repo.add_fitness_profile(
        study_id=study.id,
        clade_name="24A (JN.1)",
        basic_reproduction_number_r0=3.8,
        serial_interval_days=3.4,
        ace2_binding_affinity_shift=1.85,
        cross_neutralization_titer_fold_drop=16.8,
    )
    assert profile.id is not None
    assert profile.basic_reproduction_number_r0 == 3.8

    # 4. Fetch study
    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert len(fetched.lineages) == 2
    assert len(fetched.fitness_profiles) == 1
    assert fetched.transmission_fitness_gain_pct == 31.5

    # 5. List studies
    studies = await repo.list_studies(limit=10)
    assert len(studies) >= 1
