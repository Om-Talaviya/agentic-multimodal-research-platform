"""API integration tests for Quantum Chemistry & VQE Simulation."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_quantum_chemistry_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Get supported molecules
        res_mols = await client.get("/api/v1/quantum-chemistry/molecules", headers=auth_headers)
        assert res_mols.status_code == 200
        data_mols = res_mols.json()
        assert "molecules" in data_mols
        assert "H2" in data_mols["molecules"]

        # 2. Run VQE simulation
        payload = {
            "molecule_key": "H2",
            "ansatz_type": "UCCSD",
            "optimizer": "COBYLA",
            "max_iterations": 25,
        }
        res_sim = await client.post("/api/v1/quantum-chemistry/simulate", json=payload, headers=auth_headers)
        assert res_sim.status_code == 201
        sim_data = res_sim.json()
        assert sim_data["status"] == "success"
        assert "system_id" in sim_data
        system_id = sim_data["system_id"]
        assert sim_data["chemical_accuracy_reached"] is True

        # 3. List systems
        res_list = await client.get("/api/v1/quantum-chemistry/systems", headers=auth_headers)
        assert res_list.status_code == 200
        list_data = res_list.json()
        assert len(list_data) >= 1
        assert any(s["id"] == system_id for s in list_data)

        # 4. Get system details
        res_get = await client.get(f"/api/v1/quantum-chemistry/systems/{system_id}", headers=auth_headers)
        assert res_get.status_code == 200
        get_data = res_get.json()
        assert get_data["id"] == system_id
        assert len(get_data["ansatz_executions"]) >= 1
        assert len(get_data["energy_states"]) >= 1
