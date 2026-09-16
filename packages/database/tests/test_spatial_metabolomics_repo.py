"""
Tests for Phase 57: Spatial Metabolomics Database Repository.
"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.repositories.spatial_metabolomics_repo import SpatialMetabolomicsRepository


@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_spatial_metabolomics_repo_crud(async_session: AsyncSession):
    repo = SpatialMetabolomicsRepository(async_session)

    # 1. Create experiment
    exp = await repo.create_experiment(
        tissue_sample_id="SAM-MALDI-001",
        organ_type="Brain",
        matrix_compound="DHB",
    )
    assert exp.id is not None

    # 2. Add metabolites & flux
    await repo.add_metabolites_and_flux(
        experiment_id=exp.id,
        metabolites_data=[
            {
                "metabolite_name": "L-Lactate",
                "kegg_id": "C00186",
                "mz_ratio": 89.024,
                "spatial_zone": "Tumor Core",
                "mean_intensity_au": 4500.0,
                "fold_change_vs_normal": 4.5,
            }
        ],
        flux_data=[
            {
                "pathway_name": "Warburg Effect",
                "estimated_flux_rate": 18.0,
                "pathway_activity_score": 0.95,
                "limiting_enzyme": "LDHA",
            }
        ],
    )

    # 3. Get Experiment
    fetched = await repo.get_experiment(exp.id)
    assert fetched is not None
    assert fetched.total_metabolites_identified == 1
    assert len(fetched.metabolites) == 1
    assert len(fetched.flux_routes) == 1
