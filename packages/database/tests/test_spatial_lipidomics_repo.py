"""
Unit tests for Phase 106: Spatial Lipidomics Database Repository.
"""
import pytest
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.repositories.spatial_lipidomics_repo import SpatialLipidomicsRepository

@pytest.fixture
async def async_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.mark.asyncio
async def test_spatial_lipidomics_repo_crud(async_db: AsyncSession):
    repo = SpatialLipidomicsRepository(async_db)

    # 1. Create dataset
    ds = await repo.create_dataset(
        sample_name="Mouse-Brain-01",
        tissue_type="Brain Sagittal",
        matrix_type="DHB",
        laser_spatial_resolution_um=20.0
    )
    assert ds.id is not None
    assert ds.sample_name == "Mouse-Brain-01"

    # 2. Add lipid species
    species_id = uuid.uuid4()
    species = await repo.add_lipid_species(
        dataset_id=ds.id,
        species_data=[
            {
                "id": species_id,
                "mz_ratio": 760.585,
                "lipid_species": "PC(34:1)",
                "lipid_class": "Phosphatidylcholine",
                "adduct_type": "[M+H]+",
                "structural_formula": "C42H82NO8P",
                "mean_intensity": 85.5
            }
        ]
    )
    assert len(species) == 1

    # 3. Add spatial spots
    spots = await repo.add_spatial_spots(
        dataset_id=ds.id,
        spots_data=[
            {
                "lipid_species_id": species_id,
                "x_coord": 0,
                "y_coord": 0,
                "normalized_intensity": 92.4,
                "region_annotation": "Cortex"
            }
        ]
    )
    assert len(spots) == 1

    # 4. Fetch hydrated
    fetched = await repo.get_dataset(ds.id)
    assert fetched is not None
    assert len(fetched.lipid_species) == 1
    assert len(fetched.spatial_spots) == 1
    assert fetched.detected_lipid_classes == 1
    assert fetched.total_spots == 1
