"""Integration tests for Bio-Molecular Structure & Protein Folding API (Phase 38)."""

import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.dependencies import get_current_user, get_db_session
from database.connection import Base
from database.models.user import User as DBUser
from main import app


@pytest.fixture
async def async_test_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def mock_user():
    return DBUser(
        id=uuid.uuid4(),
        username="structural_biologist",
        email="biologist@deep-folding.org",
        password_hash="mocked",
        role="Researcher",
    )


@pytest.mark.asyncio
async def test_molecular_api_full_workflow(async_test_session: AsyncSession, mock_user: DBUser):
    async_test_session.add(mock_user)
    await async_test_session.commit()

    async def override_get_db():
        yield async_test_session

    async def override_get_user():
        return mock_user

    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Predict 3D Structure
        predict_payload = {
            "uniprot_id": "Q9BYF1",
            "gene_name": "PCSK9",
            "sequence": "MGTVSSRRSWWPLPLLL",
            "structure_source": "AlphaFold3",
            "organism": "Homo sapiens",
        }

        resp = await client.post("/api/v1/molecular/predict", json=predict_payload)
        assert resp.status_code == 201, resp.text
        data = resp.json()
        struct_id = data["id"]
        assert data["gene_name"] == "PCSK9"
        assert data["uniprot_id"] == "Q9BYF1"
        assert data["structure_source"] == "AlphaFold3"
        assert data["mean_plddt_score"] > 0
        assert len(data["binding_pockets"]) >= 1
        pocket_id = data["binding_pockets"][0]["id"]

        # 2. List Structures
        resp_list = await client.get("/api/v1/molecular/structures")
        assert resp_list.status_code == 200
        list_data = resp_list.json()
        assert len(list_data) >= 1
        assert any(s["id"] == struct_id for s in list_data)

        # 3. Get Single Structure
        resp_get = await client.get(f"/api/v1/molecular/structures/{struct_id}")
        assert resp_get.status_code == 200
        get_data = resp_get.json()
        assert get_data["id"] == struct_id
        assert len(get_data["binding_pockets"]) >= 1

        # 4. Dock Ligand
        dock_payload = {
            "pocket_id": pocket_id,
            "ligand_name": "Evolocumab Mimetic",
            "ligand_smiles": "CC(C)CC1NC(=O)C(CC2=CC=CC=C2)NC(=O)C",
        }
        resp_dock = await client.post(f"/api/v1/molecular/structures/{struct_id}/dock", json=dock_payload)
        assert resp_dock.status_code == 200, resp_dock.text
        dock_data = resp_dock.json()
        assert dock_data["ligand_name"] == "Evolocumab Mimetic"
        assert dock_data["binding_affinity_kcal_mol"] < 0
        assert dock_data["hydrogen_bonds_count"] >= 1

        # 5. Mutational Stability Scan
        mutate_payload = {
            "wildtype_residue": "D",
            "position": 374,
            "mutant_residue": "Y",
        }
        resp_mutate = await client.post(f"/api/v1/molecular/structures/{struct_id}/mutate", json=mutate_payload)
        assert resp_mutate.status_code == 200, resp_mutate.text
        mutate_data = resp_mutate.json()
        assert mutate_data["wildtype_residue"] == "D"
        assert mutate_data["position"] == 374
        assert mutate_data["mutant_residue"] == "Y"
        assert "delta_delta_g_kcal_mol" in mutate_data

        # 6. Export PDB
        resp_export = await client.get(f"/api/v1/molecular/structures/{struct_id}/export-pdb")
        assert resp_export.status_code == 200
        assert "HEADER" in resp_export.text
        assert "ATOM" in resp_export.text
        assert "END" in resp_export.text

    app.dependency_overrides.clear()
