import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.dependencies import get_current_user, get_db_session
from database.connection import Base
from database.models.user import User
from main import app


@pytest.fixture
async def api_client():
    """Create test client with in-memory SQLite and auth override."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    test_user = User(
        id=uuid.uuid4(),
        username="alignment_engineer",
        email="alignment@test.com",
        password_hash="hash",
        role="researcher",
    )

    async def override_get_db_session():
        async with async_session_factory() as session:
            yield session

    async def override_get_current_user():
        return test_user

    async with async_session_factory() as session:
        session.add(test_user)
        await session.commit()

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_dataset_synthesis_api_full_workflow(api_client: AsyncClient):
    """Test dataset synthesis, list, detail, curation, export, and metrics."""
    # 1. Synthesize Dataset
    synth_resp = await api_client.post(
        "/api/v1/datasets/synthesize",
        json={
            "name": "Sparse Attention Tuning SFT",
            "description": "Synthesized dataset on sub-quadratic transformer attention.",
            "dataset_format": "alpaca_sft",
            "domain_field": "computer_science",
            "target_model_family": "llama_3",
            "sample_count": 4,
            "topic": "Flash Attention and Sparse Kernels",
            "research_findings": [
                {"claim": "Block-sparse kernels reduce peak memory by 45%", "detail": "Verified across 128k token contexts."},
            ],
        },
    )
    assert synth_resp.status_code == 201
    dataset_data = synth_resp.json()
    dataset_id = dataset_data["id"]
    assert dataset_data["name"] == "Sparse Attention Tuning SFT"
    assert dataset_data["total_samples"] == 4

    # 2. List Datasets
    list_resp = await api_client.get("/api/v1/datasets")
    assert list_resp.status_code == 200
    datasets = list_resp.json()
    assert len(datasets) >= 1

    # 3. Get Dataset Detail
    detail_resp = await api_client.get(f"/api/v1/datasets/{dataset_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert len(detail["samples"]) == 4
    sample1_id = detail["samples"][0]["id"]

    # 4. Active Learning Curation
    curate_resp = await api_client.patch(
        f"/api/v1/datasets/{dataset_id}/samples/{sample1_id}",
        json={
            "verdict": "accepted",
            "quality_score": 0.99,
        },
    )
    assert curate_resp.status_code == 200
    assert curate_resp.json()["curation_verdict"] == "accepted"

    # 5. Export Dataset
    export_resp = await api_client.post(
        f"/api/v1/datasets/{dataset_id}/export",
        json={"export_format": "jsonl"},
    )
    assert export_resp.status_code == 201
    export_data = export_resp.json()
    assert export_data["sample_count"] == 4
    assert "preview_jsonl" in export_data

    # 6. Platform Metrics
    metrics_resp = await api_client.get("/api/v1/datasets/metrics")
    assert metrics_resp.status_code == 200
    metrics = metrics_resp.json()
    assert metrics["total_synthetic_datasets"] >= 1
    assert metrics["total_instruction_samples"] >= 4
    assert metrics["total_alignment_exports"] >= 1
