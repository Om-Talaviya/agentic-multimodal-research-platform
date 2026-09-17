import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_gene_circuit_burden_api_endpoints(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Simulate Circuit Burden
        payload = {
            "circuit_name": "API-Toggle-Switch-99",
            "host_organism": "E. coli K-12",
            "promoter_strength_rpum": 1250.0,
            "cds_length_amino_acids": 450,
            "copy_number_per_cell": 15
        }
        res = await client.post("/api/v1/circuit-burden/simulate", json=payload, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert "simulation_id" in data
        assert data["ribosome_allocation_pct"] > 0.0
        sim_id = data["simulation_id"]

        # 2. List Simulations
        res_list = await client.get("/api/v1/circuit-burden/simulations", headers=auth_headers)
        assert res_list.status_code == 200
        sims = res_list.json()
        assert len(sims) >= 1

        # 3. Get Single Simulation
        res_get = await client.get(f"/api/v1/circuit-burden/simulations/{sim_id}", headers=auth_headers)
        assert res_get.status_code == 200
        detail = res_get.json()
        assert detail["id"] == sim_id
        assert len(detail["capacity_models"]) == 1
