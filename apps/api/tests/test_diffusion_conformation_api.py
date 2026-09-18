"""API integration tests for Diffusion 3D Conformation Generation."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_diffusion_conformation_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Generate conformations
        payload = {
            "protein_pdb_id": "1HSG",
            "ligand_smiles": "CC(C)CN(CC(C)C)C(=O)NC(C(=O)NC1CCCC1)C(O)CC2=CC=CC=C2",
            "diffusion_model_variant": "DiffDock_SE3",
            "num_diffusion_timesteps": 500,
            "sampling_temperature": 1.0,
            "num_poses": 4,
        }
        res_gen = await client.post("/api/v1/diffusion-conformation/generate", json=payload, headers=auth_headers)
        assert res_gen.status_code == 201
        data_gen = res_gen.json()
        assert data_gen["status"] == "success"
        assert "id" in data_gen
        job_id = data_gen["id"]
        assert data_gen["pocket_conformations_count"] == 2
        assert data_gen["docking_poses_count"] == 4

        # 2. List jobs
        res_list = await client.get("/api/v1/diffusion-conformation/jobs", headers=auth_headers)
        assert res_list.status_code == 200
        list_data = res_list.json()
        assert len(list_data) >= 1
        assert any(j["id"] == job_id for j in list_data)

        # 3. Get job details
        res_get = await client.get(f"/api/v1/diffusion-conformation/jobs/{job_id}", headers=auth_headers)
        assert res_get.status_code == 200
        get_data = res_get.json()
        assert get_data["id"] == job_id
        assert get_data["protein_pdb_id"] == "1HSG"
        assert len(get_data["pocket_conformations"]) == 2
        assert len(get_data["docking_poses"]) == 4
