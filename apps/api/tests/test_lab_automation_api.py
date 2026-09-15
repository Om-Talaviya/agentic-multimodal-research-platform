"""Integration tests for Autonomous Laboratory Automation API (Phase 37)."""

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
        username="lead_automation_engineer",
        email="engineer@cloud-biofoundry.org",
        password_hash="mocked",
        role="Researcher",
    )


@pytest.mark.asyncio
async def test_lab_automation_api_full_workflow(async_test_session: AsyncSession, mock_user: DBUser):
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
        # 1. Compile robotic protocol
        compile_payload = {
            "protocol_name": "Automated Cas9 Transfection Array",
            "robot_platform": "Opentrons_OT2",
            "assay_type": "CRISPR_LNP_Formulation",
            "deck_slots": [
                {"slot_number": 1, "labware_type": "opentrons_96_tiprack_300ul", "reagent_name": "300uL Tips", "initial_volume_ul": 0.0},
                {"slot_number": 2, "labware_type": "corning_96_wellplate_360ul_flat", "reagent_name": "Reaction Plate", "initial_volume_ul": 100.0},
                {"slot_number": 3, "labware_type": "nest_12_reservoir_15ml", "reagent_name": "Buffer Reservoir", "initial_volume_ul": 10000.0},
            ],
            "transfer_steps": [
                {"step_index": 1, "source_slot": 3, "source_well": "A1", "target_slot": 2, "target_well": "A1", "volume_ul": 50.0, "pipette_name": "p300_single_gen2", "liquid_class": "aqueous"},
                {"step_index": 2, "source_slot": 2, "source_well": "A1", "target_slot": 2, "target_well": "A2", "volume_ul": 25.0, "pipette_name": "p300_single_gen2", "transfer_type": "mix", "liquid_class": "viscous_glycerol"},
            ],
        }

        resp = await client.post("/api/v1/lab/protocols/compile", json=compile_payload)
        assert resp.status_code == 201, resp.text
        data = resp.json()
        proto_id = data["id"]
        assert data["protocol_name"] == "Automated Cas9 Transfection Array"
        assert "from opentrons import protocol_api" in data["protocol_python_code"]
        assert data["simulation_result"]["is_valid"] is True

        # 2. List protocols
        resp_list = await client.get("/api/v1/lab/protocols")
        assert resp_list.status_code == 200
        list_data = resp_list.json()
        assert len(list_data) >= 1
        assert any(p["id"] == proto_id for p in list_data)

        # 3. Get single protocol
        resp_get = await client.get(f"/api/v1/lab/protocols/{proto_id}")
        assert resp_get.status_code == 200
        get_data = resp_get.json()
        assert len(get_data["deck_slots"]) == 3
        assert len(get_data["transfer_steps"]) == 2
        assert len(get_data["execution_traces"]) == 1

        # 4. Simulate protocol
        sim_payload = {
            "transfer_steps": [
                {"step_index": 1, "source_slot": 3, "source_well": "A1", "target_slot": 2, "target_well": "A1", "volume_ul": 100.0, "pipette_name": "p300_single_gen2", "liquid_class": "aqueous"},
            ]
        }
        resp_sim = await client.post(f"/api/v1/lab/protocols/{proto_id}/simulate", json=sim_payload)
        assert resp_sim.status_code == 200
        sim_data = resp_sim.json()
        assert sim_data["simulation_result"]["is_valid"] is True
        assert "trace_id" in sim_data

        # 5. Export code
        resp_code = await client.get(f"/api/v1/lab/protocols/{proto_id}/export-code?format=opentrons_python")
        assert resp_code.status_code == 200
        assert "def run(protocol: protocol_api.ProtocolContext):" in resp_code.text

        resp_py = await client.get(f"/api/v1/lab/protocols/{proto_id}/export-code?format=pylabrobot")
        assert resp_py.status_code == 200
        assert "from pylabrobot.liquid_handling import LiquidHandler" in resp_py.text

        resp_auto = await client.get(f"/api/v1/lab/protocols/{proto_id}/export-code?format=autoprotocol")
        assert resp_auto.status_code == 200
        assert resp_auto.json()["format"] == "autoprotocol-v1.0"

    app.dependency_overrides.clear()
