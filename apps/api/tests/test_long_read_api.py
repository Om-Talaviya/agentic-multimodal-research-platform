"""API integration tests for Long-Read Genomics & Telomere Profiling."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_long_read_genomics_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Analyze sequencing run
        payload = {
            "sample_name": "T2T_CHM13_HighCoverage",
            "platform": "PACBIO_HIFI",
            "target_gigabases": 60.0,
            "flowcell_type": "Sequel_IIe",
        }
        res_an = await client.post("/api/v1/long-read/analyze", json=payload, headers=auth_headers)
        assert res_an.status_code == 201
        data_an = res_an.json()
        assert data_an["status"] == "success"
        assert "id" in data_an
        run_id = data_an["id"]
        assert data_an["structural_variants_count"] >= 4
        assert data_an["telomere_profiles_count"] == 14

        # 2. List runs
        res_list = await client.get("/api/v1/long-read/runs", headers=auth_headers)
        assert res_list.status_code == 200
        list_data = res_list.json()
        assert len(list_data) >= 1
        assert any(r["id"] == run_id for r in list_data)

        # 3. Get run details
        res_get = await client.get(f"/api/v1/long-read/runs/{run_id}", headers=auth_headers)
        assert res_get.status_code == 200
        get_data = res_get.json()
        assert get_data["id"] == run_id
        assert get_data["sample_name"] == "T2T_CHM13_HighCoverage"
        assert len(get_data["structural_variants"]) >= 4
        assert len(get_data["telomeric_profiles"]) == 14
