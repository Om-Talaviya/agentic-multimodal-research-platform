"""Unit tests for Grant Proposal Repository (Phase 35)."""

import pytest
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from database.connection import Base
from database.models.grant_proposal import (
    DBGrantProposal,
    DBGrantSpecificAim,
    DBGrantBudgetItem,
    DBGrantReviewScorecard,
)
from database.repositories.grant_proposal_repo import GrantProposalRepository


@pytest.fixture
async def test_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_grant_proposal_crud_lifecycle(test_session: AsyncSession):
    repo = GrantProposalRepository(test_session)

    # 1. Create Proposal
    proposal = await repo.create_proposal(
        title="Autonomous In-Silico Synthesis of Quantum Materials",
        funding_agency="NIH",
        grant_mechanism="R01",
        target_call_number="PAR-24-100",
        project_duration_years=5,
        total_requested_budget_usd=1850000.0,
        indirect_cost_rate_percent=52.0,
    )
    assert proposal.id is not None
    assert proposal.status == "draft"
    assert proposal.funding_agency == "NIH"

    # 2. Add Specific Aims
    aim1 = await repo.add_specific_aim(
        proposal_id=proposal.id,
        aim_number=1,
        title="Develop closed-loop AST verification harness",
        hypothesis="Sandboxed verification eliminates false positives.",
        experimental_design="Evaluate on 10,000 synthetic material candidates.",
        expected_outcomes="Zero regression formal execution.",
        milestones_json=[{"quarter": "Q1", "milestone": "Sandbox Ready"}],
        allocated_effort_percent=40.0,
    )
    assert aim1.id is not None
    assert aim1.aim_number == 1

    # 3. Add Budget Items
    b_item = await repo.add_budget_item(
        proposal_id=proposal.id,
        year_number=1,
        category="personnel",
        item_name="PI Effort (2 months)",
        cost_usd=30000.0,
        justification="Senior oversight and project direction.",
        is_direct_cost=True,
    )
    assert b_item.id is not None
    assert b_item.cost_usd == 30000.0

    # 4. Record Mock Review Scorecard
    scorecard = await repo.record_review_scorecard(
        proposal_id=proposal.id,
        reviewer_persona="study_section_chair",
        significance_score=1.8,
        investigators_score=1.5,
        innovation_score=1.6,
        approach_score=2.0,
        environment_score=1.4,
        overall_impact_score=1.85,
        recommendation="high_priority_fund",
        critique_strengths=["Exceptional methodological innovation"],
        critique_weaknesses=["Ambitious Year 4 timeline"],
        summary_statement="Enthusiastically recommended for funding.",
    )
    assert scorecard.id is not None
    assert scorecard.overall_impact_score == 1.85

    # 5. Fetch full proposal
    fetched = await repo.get_proposal(proposal.id)
    assert fetched is not None
    assert len(fetched.aims) == 1
    assert len(fetched.budget_items) == 1
    assert len(fetched.review_scorecards) == 1
    assert fetched.status == "review_ready"
    assert fetched.percentile_estimate > 80.0

    # 6. List proposals
    proposals = await repo.list_proposals(funding_agency="NIH")
    assert len(proposals) == 1

    # 7. Delete proposal
    deleted = await repo.delete_proposal(proposal.id)
    assert deleted is True
    assert await repo.get_proposal(proposal.id) is None
