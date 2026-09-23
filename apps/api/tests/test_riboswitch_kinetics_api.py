"""API integration tests for Riboswitch Kinetics Engine (Phase 134)."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_riboswitch_kinetics_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Simulate kinetic switch
        payload = {
            "circuit_name": "Engineered Guanine Riboswitch ON-Sensor",
            "target_ligand": "Guanine",
            "rna_sequence": "GGCCACACCUGUGCUAGAGGCCCAUUGCUGUCGUGGGUGUCCAGUACGAC",
            "aptamer_class": "xpt Guanine Aptamer",
            "expression_platform_type": "Rho-Independent Terminator",
            "transcription_speed_nt_per_sec": 28.0,
            "temperature_celsius": 37.0,
        }
        res_post = await client.post("/api/v1/riboswitch-kinetics/simulate", json=payload, headers=auth_headers)
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "circuit_id" in data_post
        assert data_post["circuit_name"] == "Engineered Guanine Riboswitch ON-Sensor"
        assert data_post["dynamic_range_fold"] > 0
        circuit_id = data_post["circuit_id"]

        # 2. Retrieve circuit details
        res_get = await client.get(f"/api/v1/riboswitch-kinetics/circuits/{circuit_id}", headers=auth_headers)
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == circuit_id
        assert data_get["circuit_name"] == "Engineered Guanine Riboswitch ON-Sensor"
        assert data_get["secondary_structures_count"] == 2
        assert data_get["ligand_kinetics_count"] == 1
