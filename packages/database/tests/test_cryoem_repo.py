"""Unit tests for Cryo-EM Repository (Phase 47)."""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from database.connection import Base
from database.repositories.cryoem_repo import CryoEMRepository

@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session
    
    await engine.dispose()

@pytest.mark.asyncio
async def test_cryoem_repo_crud(async_session: AsyncSession):
    repo = CryoEMRepository(async_session)
    density_map = await repo.create_density_map(
        title="2.4A Cryo-EM Map of PCSK9-mAb",
        emdb_id="EMD-30452",
        nominal_resolution=2.4
    )
    assert density_map.id is not None
    assert density_map.status == "FITTED"

    fitting = await repo.add_fitting(
        density_map_id=density_map.id,
        pdb_model_id="7KRR",
        cross_correlation=0.89,
        molprobity_clashscore=1.8,
        ramachandran_favored_pct=98.1,
        rotamer_outliers_pct=0.3,
        alpha_helices=26,
        beta_sheets=20
    )
    assert fitting.id is not None

    comp = await repo.add_macromolecular_complex(
        density_map_id=density_map.id,
        complex_name="PCSK9-mAb Assembly",
        stoichiometry="A2B2",
        buried_surface_area=3600.0,
        binding_free_energy=-15.8,
        interface_residue_count=68,
        interaction_hotspots=[{"res_a": "Arg-142", "res_b": "Glu-88"}]
    )
    assert comp.id is not None

    fetched = await repo.get_density_map(density_map.id)
    assert len(fetched.fittings) == 1
    assert len(fetched.complexes) == 1
