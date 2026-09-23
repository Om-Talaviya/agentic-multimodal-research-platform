"""Tests for Phase 129 PanDDACrystallographyRepository."""

import pytest
import uuid
from database.repositories.pandda_crystallography_repo import PanDDACrystallographyRepository


@pytest.mark.asyncio
async def test_pandda_repo_lifecycle(db_session):
    repo = PanDDACrystallographyRepository(db_session)

    # 1. Create screen
    screen = await repo.create_screen(
        campaign_name="SARS_CoV_2_Mpro_XChem_PanDDA",
        target_protein="Main Protease (Mpro)",
        crystal_space_group="C 1 2 1",
        high_resolution_cutoff_angstrom=1.35,
        total_crystals_soaked=380,
        pandda_events_detected=18,
        background_model_r_free=0.178,
        metadata_json={"beamline": "Diamond Light Source I04-1"},
    )
    assert screen.id is not None
    assert screen.campaign_name == "SARS_CoV_2_Mpro_XChem_PanDDA"

    # 2. Add fragment hit
    hit = await repo.add_fragment_hit(
        screen_id=screen.id,
        hit_id="XChem_Mpro_Hit_042",
        fragment_smiles="CC(=O)Nc1ccc(S(=O)(=O)N)cc1",
        binding_site_name="Catalytic Cys145-His41 Dyad",
        event_b_factor=22.4,
        event_occupancy=0.82,
        z_peak_score=7.12,
        ligand_efficiency_le=0.52,
    )
    assert hit.id is not None
    assert hit.hit_id == "XChem_Mpro_Hit_042"

    # 3. Add density map
    dmap = await repo.add_density_map(
        screen_id=screen.id,
        map_id="PanDDA_Ground_State_Model_01",
        resolution_angstrom=1.35,
        statistical_outlier_noise_sigma=0.08,
        mean_density_value=1.02,
    )
    assert dmap.id is not None
    assert dmap.map_id == "PanDDA_Ground_State_Model_01"

    # 4. Get screen
    fetched = await repo.get_screen(screen.id)
    assert fetched is not None
    assert len(fetched.hits) == 1
    assert len(fetched.density_maps) == 1
    assert fetched.hits[0].hit_id == "XChem_Mpro_Hit_042"

    # 5. List screens
    screens = await repo.list_screens(limit=10)
    assert len(screens) >= 1
