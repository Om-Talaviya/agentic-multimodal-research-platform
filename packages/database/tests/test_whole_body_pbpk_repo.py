"""Tests for Whole-Body PBPK Database Repository."""

import pytest
from database.connection import AsyncSession
from database.repositories.whole_body_pbpk_repo import WholeBodyPBPKRepository


@pytest.mark.asyncio
async def test_whole_body_pbpk_repo_crud(db_session: AsyncSession) -> None:
    repo = WholeBodyPBPKRepository(db_session)

    study = await repo.create_study(
        study_name="Test PBPK Investigation",
        drug_candidate_name="TEST-DRUG-001",
        molecular_weight_da=410.5,
        logp=3.1,
        plasma_protein_unbound_fraction=0.05,
        intrinsic_clearance_ml_min_kg=12.0,
        species="human",
        administration_route="oral",
        dose_mg_kg=5.0,
        simulation_time_hours=24.0,
        summary_metrics={"steady_state_volume_of_distribution_l_kg": 2.45},
        compartments=[
            {
                "organ_name": "liver",
                "organ_volume_l_kg": 0.026,
                "blood_flow_rate_l_h_kg": 1.25,
                "tissue_plasma_partition_coefficient": 3.4,
                "permeability_surface_area_product": 1.2,
                "computed_cmax_ug_ml": 4.5,
                "computed_auc_ug_h_ml": 22.0,
                "computed_tmax_h": 1.2,
            }
        ],
        clearance_rates=[
            {
                "elimination_pathway": "hepatic_cyp_metabolism",
                "organ_source": "liver",
                "clearance_rate_ml_min": 320.0,
                "extraction_ratio": 0.35,
                "fraction_metabolized": 0.85,
            }
        ],
    )

    assert study.id is not None
    assert study.study_name == "Test PBPK Investigation"
    assert len(study.organ_compartments) == 1
    assert len(study.clearance_rates) == 1

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.drug_candidate_name == "TEST-DRUG-001"

    studies = await repo.list_studies()
    assert len(studies) >= 1

    deleted = await repo.delete_study(study.id)
    assert deleted is True

    empty = await repo.get_study(study.id)
    assert empty is None
