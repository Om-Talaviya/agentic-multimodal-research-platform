"""Integration tests for Generative Chemistry REST API (Phase 43)."""
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.connection import Base
from database.models.user import User as DBUser
from api.dependencies import get_current_user, get_db_session
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
        username="chemoinformatics_lead",
        email="chem_lead@novartis.com",
        password_hash="mocked",
        role="Researcher",
    )

@pytest.mark.asyncio
async def test_generative_chemistry_api_lifecycle(async_test_session: AsyncSession, mock_user: DBUser):
    async def override_get_db():
        yield async_test_session

    async def override_get_user():
        return mock_user

    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. POST /api/v1/chemistry/generate-molecules
        req_mol = {
            "target_protein": "KRAS-G12D",
            "n_candidates": 3
        }
        res_mol = await client.post("/api/v1/chemistry/generate-molecules", json=req_mol)
        assert res_mol.status_code == 201
        mols = res_mol.json()
        assert len(mols) == 3
        assert mols[0]["target_protein"] == "KRAS-G12D"
        mol_id = mols[0]["id"]

        # 2. GET /api/v1/chemistry/molecules
        res_list = await client.get("/api/v1/chemistry/molecules")
        assert res_list.status_code == 200
        assert len(res_list.json()) >= 3

        # 3. POST /api/v1/chemistry/optimize-antibody
        req_ab = {
            "antigen_target": "CLDN18.2",
            "n_mutants": 2
        }
        res_ab = await client.post("/api/v1/chemistry/optimize-antibody", json=req_ab)
        assert res_ab.status_code == 201
        abs_list = res_ab.json()
        assert len(abs_list) == 2
        assert abs_list[0]["antigen_target"] == "CLDN18.2"

        # 4. GET /api/v1/chemistry/antibodies
        res_ab_list = await client.get("/api/v1/chemistry/antibodies")
        assert res_ab_list.status_code == 200
        assert len(res_ab_list.json()) >= 2

        # 5. DELETE /api/v1/chemistry/molecules/{id}
        res_del = await client.delete(f"/api/v1/chemistry/molecules/{mol_id}")
        assert res_del.status_code == 204

    app.dependency_overrides.clear()
