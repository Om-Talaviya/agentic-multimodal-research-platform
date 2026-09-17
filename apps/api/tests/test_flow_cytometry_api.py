import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_flow_cytometry_api_endpoints(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Analyze Flow Run
        payload = {
            "experiment_name": "CAR-T Phenotyping",
            "sample_id": "SMP-FLOW-TEST-99",
            "cell_type": "CAR-T",
            "total_event_count": 50000,
            "gating_steps": [
                {
                    "gate_name": "Lymphocytes",
                    "x_channel": "FSC-A",
                    "y_channel": "SSC-A",
                    "polygon_vertices": [[20000, 10000], [60000, 10000], [60000, 50000], [20000, 50000]],
                    "synthetic_retention_rate": 0.82
                },
                {
                    "gate_name": "Live Cells",
                    "x_channel": "CD3-FITC",
                    "y_channel": "Live/Dead",
                    "polygon_vertices": [[1000, 100], [100000, 100], [100000, 2000], [1000, 2000]],
                    "synthetic_retention_rate": 0.94
                }
            ],
            "positive_controls": [95.0, 94.8, 95.5, 96.0, 94.7],
            "negative_controls": [4.0, 3.8, 4.2, 3.9, 4.1],
            "plate_id": "PLT-384-HTS-API"
        }
        res = await client.post("/api/v1/flow-cytometry/analyze", json=payload, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert "experiment_id" in data
        assert data["z_prime_factor"] >= 0.70
        exp_id = data["experiment_id"]

        # 2. List Experiments
        res_list = await client.get("/api/v1/flow-cytometry/experiments", headers=auth_headers)
        assert res_list.status_code == 200
        exps = res_list.json()
        assert len(exps) >= 1

        # 3. Get Single Experiment
        res_get = await client.get(f"/api/v1/flow-cytometry/experiments/{exp_id}", headers=auth_headers)
        assert res_get.status_code == 200
        detail = res_get.json()
        assert detail["id"] == exp_id
        assert len(detail["gates"]) == 2
        assert len(detail["z_prime_metrics"]) == 1
