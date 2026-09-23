"""Tests for Phase 130 AdaptiveResistanceRepository."""

import pytest
from database.repositories.adaptive_resistance_repo import AdaptiveResistanceRepository


@pytest.mark.asyncio
async def test_adaptive_resistance_repo_lifecycle(db_session):
    repo = AdaptiveResistanceRepository(db_session)

    # 1. Create study
    study = await repo.create_study(
        name="TNBC Cisplatin Adaptive Study",
        cancer_type="Triple-Negative Breast Cancer",
        patient_id="PT-90210",
        description="Longitudinal clonal fitness simulation under dose-modulated Cisplatin",
        chemo_regimen=[{"drug": "Cisplatin", "base_dose_mg_m2": 75, "cycle_days": 21}],
        total_cycles=6,
        summary_metrics={"max_resistance_index": 0.42, "extinction_events": 1},
    )
    assert study.id is not None
    assert study.name == "TNBC Cisplatin Adaptive Study"
    assert study.total_cycles == 6

    # 2. Add clonal lineages
    clone1 = await repo.add_clonal_lineage(
        study_id=study.id,
        clone_name="Clone_A_WildType",
        driver_mutations=["TP53_R273H"],
        initial_frequency=0.85,
        final_frequency=0.15,
        intrinsic_fitness=1.0,
        drug_ic50_shifts={"Cisplatin": 1.0},
        phenotype="SENSITIVE",
    )
    clone2 = await repo.add_clonal_lineage(
        study_id=study.id,
        clone_name="Clone_B_BRCA1_Reversion",
        driver_mutations=["TP53_R273H", "BRCA1_C61G_Rev"],
        initial_frequency=0.15,
        final_frequency=0.85,
        intrinsic_fitness=1.35,
        drug_ic50_shifts={"Cisplatin": 8.5},
        phenotype="MULTI_DRUG_RESISTANT",
    )
    assert clone1.id is not None
    assert clone2.phenotype == "MULTI_DRUG_RESISTANT"

    lineages = await repo.get_lineages_by_study(study.id)
    assert len(lineages) == 2

    # 3. Add longitudinal trajectory
    traj0 = await repo.add_trajectory_point(
        study_id=study.id,
        time_step=0,
        drug_concentration=75.0,
        tumor_burden=1.0,
        clone_abundances={"Clone_A_WildType": 0.85, "Clone_B_BRCA1_Reversion": 0.15},
        resistance_index=0.15,
        adaptive_recommendation="CONTINUE",
    )
    traj1 = await repo.add_trajectory_point(
        study_id=study.id,
        time_step=1,
        drug_concentration=50.0,
        tumor_burden=0.62,
        clone_abundances={"Clone_A_WildType": 0.50, "Clone_B_BRCA1_Reversion": 0.50},
        resistance_index=0.50,
        adaptive_recommendation="DOSE_MODULATE",
    )
    assert traj0.id is not None
    assert traj1.time_step == 1

    trajs = await repo.get_trajectories_by_study(study.id)
    assert len(trajs) == 2
    assert trajs[0].time_step == 0
    assert trajs[1].adaptive_recommendation == "DOSE_MODULATE"

    # 4. List studies
    studies = await repo.list_studies()
    assert len(studies) >= 1
    fetched = await repo.get_study(study.id)
    assert fetched.patient_id == "PT-90210"
