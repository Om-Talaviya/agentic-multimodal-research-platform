"""API integration tests for Whole-Cell Metabolism endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_whole_cell_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Get presets
        res_pre = await client.get("/api/v1/whole-cell/presets", headers=auth_headers)
        assert res_pre.status_code == 200
        assert "models" in res_pre.json()

        # 2. Simulate Whole-Cell FBA
        payload = {
            "model_id": "iML1515",
            "carbon_source": "GLUCOSE",
            "initial_glucose_g_L": 20.0,
            "initial_biomass_g_L": 0.1,
            "simulation_duration_hours": 8.0,
            "time_step_hours": 2.0,
        }
        res_sim = await client.post("/api/v1/whole-cell/simulate", json=payload, headers=auth_headers)
        assert res_sim.status_code == 201
        data_sim = res_sim.json()
        assert data_sim["status"] == "success"
        assert "id" in data_sim
        model_id = data_sim["id"]
        assert data_sim["flux_states_count"] >= 6
        assert data_sim["simulation_traces_count"] == 5

        # 3. List models
        res_list = await client.get("/api/v1/whole-cell/models", headers=auth_headers)
        assert res_list.status_code == 200
        list_data = res_list.json()
        assert len(list_data) >= 1
        assert any(m["id"] == model_id for m in list_data)

        # 4. Get model details
        res_get = await client.get(f"/api/v1/whole-cell/models/{model_id}", headers=auth_headers)
        assert res_get.status_code == 200
        get_data = res_get.json()
        assert get_data["id"] == model_id
        assert len(get_data["flux_states"]) >= 6
        assert len(get_data["simulation_traces"]) == 5
