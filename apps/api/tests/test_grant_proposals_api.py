"""Integration tests for Grant Proposal REST API routes (Phase 35)."""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from api.dependencies import get_db_session
from database.connection import Base
from main import app


@pytest_asyncio.fixture
async def client_with_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db_session():
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except BaseException:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = override_get_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_grant_proposal_api_full_workflow(client_with_db: AsyncClient):
    # 1. Create Proposal
    create_payload = {
        "title": "Autonomous Multi-Agent Scientific Discovery Platform",
        "funding_agency": "NIH",
        "grant_mechanism": "R01",
        "target_call_number": "PAR-24-112",
        "project_duration_years": 5,
        "total_requested_budget_usd": 1500000.0,
        "indirect_cost_rate_percent": 52.0,
    }
    res = await client_with_db.post("/api/v1/grants/proposals", json=create_payload)
    assert res.status_code == 201
    proposal = res.json()
    proposal_id = proposal["id"]
    assert proposal["title"] == create_payload["title"]
    assert proposal["funding_agency"] == "NIH"

    # 2. List Proposals
    res_list = await client_with_db.get("/api/v1/grants/proposals")
    assert res_list.status_code == 200
    proposals_list = res_list.json()
    assert len(proposals_list) == 1

    # 3. Synthesize Proposal Narratives & Specific Aims
    synth_payload = {
        "research_topic": "Autonomous quantum chemistry and in-silico reproducibility",
        "key_findings": ["Coupling constant verified with 0.007% delta"],
    }
    res_synth = await client_with_db.post(f"/api/v1/grants/proposals/{proposal_id}/synthesize", json=synth_payload)
    assert res_synth.status_code == 200
    synthesized_prop = res_synth.json()
    assert synthesized_prop["executive_abstract"] is not None
    assert len(synthesized_prop["aims"]) == 3

    # 4. Calculate Institutional Multi-Year Budget
    budget_payload = {
        "duration_years": 5,
        "pi_base_salary": 180000.0,
        "pi_effort_months": 2.0,
        "postdoc_count": 1,
        "postdoc_base_salary": 65000.0,
        "grad_student_count": 2,
        "grad_student_stipend": 38000.0,
        "equipment_cost_y1": 100000.0,
        "cloud_compute_annual": 40000.0,
        "supplies_annual": 20000.0,
        "travel_annual": 10000.0,
        "fringe_rate_percent": 28.5,
        "indirect_rate_percent": 52.0,
        "annual_escalation_percent": 3.0,
    }
    res_budget = await client_with_db.post(f"/api/v1/grants/proposals/{proposal_id}/budget/calculate", json=budget_payload)
    assert res_budget.status_code == 200
    budget_data = res_budget.json()
    assert budget_data["total_requested_budget"] > 0.0
    assert len(budget_data["yearly_breakdowns"]) == 5

    # 5. Conduct Mock Study Section Review
    res_score = await client_with_db.post(f"/api/v1/grants/proposals/{proposal_id}/score-mock-panel")
    assert res_score.status_code == 200
    scorecard = res_score.json()
    assert scorecard["overall_impact_score"] >= 1.0
    assert scorecard["overall_impact_score"] <= 9.0

    # 6. Export LaTeX Grant Document
    res_latex = await client_with_db.get(f"/api/v1/grants/proposals/{proposal_id}/export-latex")
    assert res_latex.status_code == 200
    latex_resp = res_latex.json()
    assert "\\documentclass" in latex_resp["latex_content"]
    assert "\\section{1. Specific Aims}" in latex_resp["latex_content"]
