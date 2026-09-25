"""Tests for Phase 184: Fragment-Based Lead Discovery Repository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.fragment_based_lead_discovery_repo import FBDDLeadDiscoveryRepository


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
async def test_fragment_based_lead_discovery_repo_crud(async_db: AsyncSession):
    repo = FBDDLeadDiscoveryRepository(async_db)

    study = await repo.create_study(
        name="KRAS-G12D Test Study",
        target_protein_pocket="KRAS-G12D Switch-II Pocket",
        fragment_library_size=1500,
        top_fragment_kd_micromolar=42.5,
        mean_ligand_efficiency=0.38,
        optimized_lead_predicted_pic50=8.45,
    )
    await async_db.commit()

    assert study.id is not None
    assert study.target_protein_pocket == "KRAS-G12D Switch-II Pocket"

    hit = await repo.add_fragment_hit(
        study_id=study.id,
        fragment_id="FRAG-KRAS-01",
        smiles_representation="c1ccc(NC(=O)C)cc1",
        heavy_atom_count=10,
        molecular_weight_da=135.16,
        dissociation_constant_kd_um=45.0,
        ligand_efficiency_le=0.41,
        subpocket_binding_site="Switch-II Subpocket-1",
    )
    await async_db.commit()

    assert hit.id is not None
    assert hit.fragment_id == "FRAG-KRAS-01"

    candidate = await repo.add_linker_candidate(
        study_id=study.id,
        lead_id="LEAD-FBDD-OPT-01",
        combined_smiles="CC(=O)Nc1ccc(cc1)-C#C-c2cncc(O)c2",
        linker_type="alkyne_rigid_spacer_3A",
        predicted_affinity_kd_nm=18.4,
        binding_delta_g_kcal_mol=-10.6,
        synthetic_accessibility_sa_score=2.35,
    )
    await async_db.commit()

    assert candidate.id is not None

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "KRAS-G12D Test Study"

    studies = await repo.list_studies()
    assert len(studies) >= 1