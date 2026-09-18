"""Tests for Phenotypic Screening repository."""

import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.phenotypic_screening_repo import PhenotypicScreeningRepository


@pytest.mark.asyncio
async def test_phenotypic_screening_repo_crud(db_session: AsyncSession):
    repo = PhenotypicScreeningRepository(db_session)
    ws_id = uuid.uuid4()

    # 1. Create plate
    plate = await repo.create_plate(
        workspace_id=ws_id,
        plate_name="CellPainting_Plate_Alpha",
        format="384-well",
        cell_line="HeLa",
        imaging_magnification="40x",
        channels_profiled=["DNA", "RNA", "ER", "AGP", "Mito"],
        total_wells=1,
    )
    assert plate.id is not None
    assert plate.plate_name == "CellPainting_Plate_Alpha"
    assert plate.cell_line == "HeLa"

    # 2. Add well with single-cell morphometry
    single_cells = [
        {
            "cell_index": 1,
            "nuclear_area": 165.2,
            "nuclear_eccentricity": 0.44,
            "cytoplasm_area": 490.5,
            "er_intensity_mean": 1210.0,
            "mito_texture_contrast": 34.5,
            "actin_alignment_index": 0.71,
            "zernike_moment_z20": 0.14,
            "haralick_homogeneity": 0.83,
        }
    ]

    well = await repo.add_well_profile(
        plate_id=plate.id,
        well_position="A01",
        compound_name="Brefeldin A",
        concentration_uM=5.0,
        is_control=False,
        cell_count=1,
        viability_pct=92.0,
        predicted_moa="Proteasome Inhibitor",
        moa_confidence=0.91,
        phenotypic_activity_score=3.4,
        morphological_profile={"er_intensity_au": 1210.0},
        single_cells=single_cells,
    )
    assert well.id is not None
    assert well.compound_name == "Brefeldin A"
    assert well.predicted_moa == "Proteasome Inhibitor"

    # 3. Retrieve plate with wells and single cells
    fetched_plate = await repo.get_plate(plate.id)
    assert fetched_plate is not None
    assert len(fetched_plate.wells) == 1
    assert len(fetched_plate.wells[0].single_cells) == 1

    fetched_well = await repo.get_well(well.id)
    assert fetched_well is not None
    assert len(fetched_well.single_cells) == 1
    assert fetched_well.single_cells[0].nuclear_area == 165.2

    # 4. List plates
    plates = await repo.list_plates(ws_id)
    assert len(plates) == 1
    assert plates[0].id == plate.id
