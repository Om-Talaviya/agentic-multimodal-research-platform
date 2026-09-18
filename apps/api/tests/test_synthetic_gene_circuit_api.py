"""API integration tests for Synthetic Biology Gene Circuit Design."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_synthetic_gene_circuit_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Get parts library
        res_parts = await client.get("/api/v1/synthetic-gene-circuits/parts", headers=auth_headers)
        assert res_parts.status_code == 200
        data_parts = res_parts.json()
        assert "parts" in data_parts
        assert "pTet" in data_parts["parts"]

        # 2. Design circuit
        payload = {
            "circuit_name": "CAR_T_Logic_Gate_01",
            "logic_function": "AND",
            "chassis_organism": "Escherichia coli K-12",
            "output_reporter": "sfGFP",
        }
        res_post = await client.post("/api/v1/synthetic-gene-circuits/design", json=payload, headers=auth_headers)
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "success"
        assert "circuit_id" in data_post
        assert data_post["gates_count"] >= 2
        circuit_id = data_post["circuit_id"]

        # 3. Retrieve circuit details
        res_get = await client.get(f"/api/v1/synthetic-gene-circuits/circuits/{circuit_id}", headers=auth_headers)
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == circuit_id
        assert data_get["circuit_name"] == "CAR_T_Logic_Gate_01"
        assert len(data_get["gates"]) >= 2
        assert len(data_get["kinetics_traces"]) == 4
