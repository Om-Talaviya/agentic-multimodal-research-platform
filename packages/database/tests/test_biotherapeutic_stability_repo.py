import pytest
import pytest_asyncio
from database.models.biotherapeutic_stability import DBBiotherapeuticConstruct
from database.repositories.biotherapeutic_stability_repo import BiotherapeuticStabilityRepository

@pytest.mark.asyncio
async def test_biotherapeutic_stability_repository(async_db_session):
    repo = BiotherapeuticStabilityRepository(async_db_session)

    # 1. Create construct
    construct = await repo.create_construct(
        construct_name="Trastuzumab-Bio-01",
        modality="mAb",
        heavy_chain_sequence="EVQLVESGGGLVQPGGSLRLSCAASGFNIKDTYIHWVRQAPGKGLEWVARIYPTNGYTRYADSVKG",
        light_chain_sequence="DIQMTQSPSSLSASVGDRVTITCRASQDVNTAVAWYQQKPGKAPKLLIYSASFLYSGVPSRFSG",
        melting_temp_tm1_celsius=72.5,
        melting_temp_tm2_celsius=83.0,
        aggregation_propensity_score=0.15,
    )
    assert construct.id is not None
    assert construct.construct_name == "Trastuzumab-Bio-01"

    # 2. Add hydrophobic patch
    patch = await repo.add_hydrophobic_patch(
        construct_id=construct.id,
        patch_identifier="CDR-H3 Core",
        surface_area_angstrom2=220.5,
        average_hydrophobicity_score=2.15,
        residue_span="HC: 98-106",
        aggregation_risk_level="MODERATE",
    )
    assert patch.id is not None
    assert patch.construct_id == construct.id

    # 3. Add excipient screen
    screen = await repo.add_excipient_screen(
        construct_id=construct.id,
        buffer_type="Histidine",
        ph=6.0,
        surfactant="Polysorbate 80",
        tonicity_agent="Sucrose",
        monomer_retention_pct_at_40c=97.8,
    )
    assert screen.id is not None

    # 4. Fetch hydrated construct
    fetched = await repo.get_construct_by_id(construct.id)
    assert fetched is not None
    assert len(fetched.hydrophobic_patches) == 1
    assert len(fetched.excipient_screens) == 1
    assert fetched.hydrophobic_patches[0].patch_identifier == "CDR-H3 Core"
