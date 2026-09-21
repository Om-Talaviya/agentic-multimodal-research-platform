"""Tests for Phase 120."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_multiome_joint_api_lifecycle(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"sample_identifier": "PBMC_10k_Multiome_ATAC_RNA", "total_cells": 12400}
        res = await client.post("/api/v1/multiome-joint/embed", json=payload, headers=auth_headers)
        assert res.status_code == 201
        did = res.json()["dataset_id"]
        res_get = await client.get(f"/api/v1/multiome-joint/datasets/{did}", headers=auth_headers)
        assert res_get.status_code == 200
