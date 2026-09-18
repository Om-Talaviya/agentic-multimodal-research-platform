"""API integration tests for Robotic Workcell & Automation endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_robotic_workcell_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Get Platforms
        res_plat = await client.get("/api/v1/robotic-workcell/platforms", headers=auth_headers)
        assert res_plat.status_code == 200
        assert "platforms" in res_plat.json()

        # 2. Compile Protocol
        payload = {
            "protocol_name": "Kinase Inhibitor IC50 Serial Dilution",
            "platform": "OPENTRONS_OT2",
            "liquid_class": "WATER_FREE",
            "samples_count": 96,
            "transfer_volume_ul": 25.0,
        }
        res_comp = await client.post("/api/v1/robotic-workcell/compile", json=payload, headers=auth_headers)
        assert res_comp.status_code == 201
        data_comp = res_comp.json()
        assert data_comp["status"] == "success"
        assert "id" in data_comp
        proto_id = data_comp["id"]
        assert data_comp["deck_layout_count"] == 4
        assert data_comp["run_executions_count"] == 1

        # 3. List Protocols
        res_list = await client.get("/api/v1/robotic-workcell/protocols", headers=auth_headers)
        assert res_list.status_code == 200
        list_data = res_list.json()
        assert len(list_data) >= 1
        assert any(p["id"] == proto_id for p in list_data)

        # 4. Get Protocol Details
        res_get = await client.get(f"/api/v1/robotic-workcell/protocols/{proto_id}", headers=auth_headers)
        assert res_get.status_code == 200
        get_data = res_get.json()
        assert get_data["id"] == proto_id
        assert get_data["protocol_name"] == "Kinase Inhibitor IC50 Serial Dilution"
        assert len(get_data["deck_layout"]) == 4
        assert len(get_data["run_executions"]) == 1
        assert "opentrons" in get_data["compiled_python_script"]
