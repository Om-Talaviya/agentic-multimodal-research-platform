"""Integration tests for Autonomous Molecular Dynamics & Quantum Chemistry API (Phase 39)."""

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
        username="computational_biophysicist",
        email="biophysicist@md-quantum.org",
        password_hash="mocked",
        role="Researcher",
    )


@pytest.mark.asyncio
async def test_molecular_dynamics_api_workflow(async_test_session: AsyncSession, mock_user: DBUser):
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
        # 1. Run MD Simulation
        simulate_payload = {
            "uniprot_id": "Q9BYF1",
            "system_name": "PCSK9 Catalytic Subdomain Solvated Complex",
            "organism": "Homo sapiens",
            "forcefield": "AMBER14SB",
            "solvent_model": "TIP3P",
            "ensemble": "NPT",
            "total_duration_ns": 50.0,
            "total_frames": 10,
            "temperature_kelvin": 300.0,
            "pressure_bar": 1.013,
        }
        res = await client.post("/api/v1/md/simulate", json=simulate_payload)
        assert res.status_code == 201, res.text
        sim_data = res.json()
        assert sim_data["id"] is not None
        assert sim_data["system_name"] == "PCSK9 Catalytic Subdomain Solvated Complex"
        assert sim_data["frames_count"] == 10
        assert sim_data["residue_fluctuations_count"] > 0
        assert sim_data["quantum_properties"]["bandgap_energy_ev"] > 0.0
        sim_id = sim_data["id"]

        # 2. List Simulations
        res = await client.get("/api/v1/md/simulations")
        assert res.status_code == 200
        sim_list = res.json()
        assert len(sim_list) >= 1
        assert any(s["id"] == sim_id for s in sim_list)

        # 3. Get Detailed Simulation
        res = await client.get(f"/api/v1/md/simulations/{sim_id}")
        assert res.status_code == 200
        detailed = res.json()
        assert detailed["id"] == sim_id
        assert detailed["equilibrium_rmsd_angstrom"] > 0.0
        assert len(detailed["trajectory_frames"]) == 10

        # 4. Get Frame Snapshot
        res = await client.get(f"/api/v1/md/simulations/{sim_id}/frames/1")
        assert res.status_code == 200
        frame = res.json()
        assert frame["frame_index"] == 1
        assert "HEADER" in frame["pdb_coordinates"]

        # 5. Export Multi-Model Trajectory PDB
        res = await client.get(f"/api/v1/md/simulations/{sim_id}/export-trajectory")
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("chemical/x-pdb")
        assert "MODEL" in res.text
        assert "ENDMDL" in res.text

    app.dependency_overrides.clear()
