"""Tests for SpatialProteomicsCODEXRepository (Phase 155)."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.spatial_proteomics_codex_repo import SpatialProteomicsCODEXRepository


@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_spatial_proteomics_codex_repo_lifecycle(async_db: AsyncSession):
    repo = SpatialProteomicsCODEXRepository(async_db)

    study = await repo.create_study(
        tissue_sample_name="Melanoma-Core-01",
        organ_tissue_type="Skin / Tumor",
        multiplex_panel_size=40,
        single_cells_segmented=8000,
        cellular_neighborhoods_count=5,
        mean_signal_to_background=26.4,
        immune_infiltration_score=0.82,
    )
    assert study.id is not None

    await repo.add_marker_expression(
        study_id=study.id,
        marker_name="CD8a",
        cellular_compartment="Membrane",
        mean_fluorescence_intensity=12000.0,
        signal_to_noise_ratio=28.0,
        positive_cells_percentage=20.0,
    )

    await repo.add_neighborhood_phenotype(
        study_id=study.id,
        neighborhood_cluster_id=1,
        neighborhood_name="Infiltration Front",
        dominant_cell_type="CD8+ T Cells",
        radius_um=50.0,
        cell_density_per_mm2=4000.0,
        immunosuppression_index=0.25,
    )

    loaded = await repo.get_study_with_details(study.id)
    assert loaded is not None
    assert len(loaded.marker_expressions) == 1
    assert len(loaded.neighborhood_phenotypes) == 1
