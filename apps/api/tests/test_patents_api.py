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
        username="patent_attorney",
        email="patent@test.com",
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
async def test_patents_api_full_workflow(api_client: AsyncClient):
    """Test patent corpus creation, indexing, 102/103 claim evaluation, FTO report, and metrics."""
    # 1. Create Corpus & Index Baseline Patents
    create_resp = await api_client.post(
        "/api/v1/patents/corpora",
        json={
            "title": "Quantum Error Correction Topological Codes",
            "technology_domain": "quantum_error_correction",
            "cpc_classification": "G06N 10/00",
            "jurisdiction": "GLOBAL",
            "sample_patent_count": 3,
        },
    )
    assert create_resp.status_code == 201
    corpus_data = create_resp.json()
    corpus_id = corpus_data["id"]
    assert corpus_data["title"] == "Quantum Error Correction Topological Codes"
    assert corpus_data["total_patents_indexed"] == 3

    # 2. List Corpora
    list_resp = await api_client.get("/api/v1/patents/corpora")
    assert list_resp.status_code == 200
    corpora = list_resp.json()
    assert len(corpora) >= 1

    # 3. Get Corpus Detail
    detail_resp = await api_client.get(f"/api/v1/patents/corpora/{corpus_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert len(detail["patents"]) == 3
    assert len(detail["patents"][0]["claims"]) >= 1

    # 4. Evaluate Claim (35 U.S.C. 102/103 Prior Art Search)
    eval_resp = await api_client.post(
        f"/api/v1/patents/corpora/{corpus_id}/evaluate-claim",
        json={
            "target_invention_claim": "A method of quantum decoding comprising: syndromic graph matching; minimum weight calculations; and parallel cluster boundary updates.",
        },
    )
    assert eval_resp.status_code == 201
    eval_data = eval_resp.json()
    assert "verdict" in eval_data
    assert "novelty_score" in eval_data
    assert "claim_chart" in eval_data

    # 5. Generate Freedom to Operate (FTO) Report
    fto_resp = await api_client.post(
        f"/api/v1/patents/corpora/{corpus_id}/fto-report",
        json={
            "target_claims": [
                "A quantum stabilizer circuit comprising: syndrome measurements; and automated error correction.",
            ],
        },
    )
    assert fto_resp.status_code == 201
    fto_data = fto_resp.json()
    assert fto_data["fto_clearance_percentage"] >= 50.0
    assert len(fto_data["white_space_opportunities"]) >= 1

    # 6. Platform Metrics
    metrics_resp = await api_client.get("/api/v1/patents/metrics")
    assert metrics_resp.status_code == 200
    metrics = metrics_resp.json()
    assert metrics["total_patent_corpora"] >= 1
    assert metrics["total_patents_indexed"] >= 3
    assert metrics["total_prior_art_evaluations"] >= 1
    assert metrics["total_fto_reports"] >= 1
