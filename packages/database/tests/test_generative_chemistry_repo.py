"""Unit tests for Generative Chemistry Repository (Phase 43)."""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from database.connection import Base
from database.repositories.generative_chemistry_repo import GenerativeChemistryRepository

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
async def test_generative_chemistry_repo_crud(async_session: AsyncSession):
    repo = GenerativeChemistryRepository(async_session)

    # 1. Create Molecule
    mol = await repo.create_molecule(
        name="PCSK9-GEN-001",
        target_protein="PCSK9",
        smiles="CC1=CC(=C(C=C1)S(=O)(=O)NC2=CC=C(C=C2)F)NC3=NC=NC4=CC(=C(C=C34)OC)OC",
        molecular_weight=442.5,
        log_p=2.85,
        qed_score=0.895,
        synthetic_accessibility=2.4,
        predicted_binding_affinity=-9.85,
    )
    assert mol.id is not None
    assert mol.name == "PCSK9-GEN-001"
    assert mol.predicted_binding_affinity == -9.85

    # 2. Add ADMET
    admet = await repo.create_admet_profile(
        molecule_id=mol.id,
        human_intestinal_absorption=94.5,
        blood_brain_barrier_permeability=0.32,
    )
    assert admet.id is not None
    assert admet.human_intestinal_absorption == 94.5

    # 3. Create Antibody
    ab = await repo.create_antibody(
        variant_name="mAb-PDL1-v1",
        antigen_target="PD-L1",
        heavy_chain_seq="EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCARDLLGWYYGMDVWWGQGTLVTVSS",
        light_chain_seq="DIQMTQSPSSLSASVGDRVTITCRASQSISSYLNWYQQKPGKAPKLLIYAASSLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQQSYSTPRTFGQGTKVEIK",
        cdr_h3_sequence="CARDLLGWYYGMDVW",
        kd_affinity_nm=0.185,
    )
    assert ab.id is not None
    assert ab.kd_affinity_nm == 0.185

    # 4. List
    mols = await repo.list_molecules(target_protein="PCSK9")
    assert len(mols) == 1
    abs_list = await repo.list_antibodies(antigen_target="PD-L1")
    assert len(abs_list) == 1

    # 5. Delete
    deleted = await repo.delete_molecule(mol.id)
    assert deleted is True
