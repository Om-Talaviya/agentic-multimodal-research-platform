"""Repository for Autonomous Scientific Grant & Research Proposal Engine (Phase 35)."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.grant_proposal import (
    DBGrantBudgetItem,
    DBGrantProposal,
    DBGrantReviewScorecard,
    DBGrantSpecificAim,
)


class GrantProposalRepository:
    """Async database repository for grant proposals, specific aims, budgets, and mock review scorecards."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_proposal(
        self,
        title: str,
        funding_agency: str = "NIH",
        grant_mechanism: str = "R01",
        target_call_number: Optional[str] = None,
        project_duration_years: int = 5,
        total_requested_budget_usd: float = 1500000.0,
        indirect_cost_rate_percent: float = 52.0,
        user_id: Optional[uuid.UUID] = None,
        workspace_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        research_job_id: Optional[uuid.UUID] = None,
        metadata_json: Optional[Dict[str, Any]] = None,
    ) -> DBGrantProposal:
        proposal = DBGrantProposal(
            id=uuid.uuid4(),
            title=title,
            funding_agency=funding_agency,
            grant_mechanism=grant_mechanism,
            target_call_number=target_call_number,
            project_duration_years=project_duration_years,
            total_requested_budget_usd=total_requested_budget_usd,
            indirect_cost_rate_percent=indirect_cost_rate_percent,
            user_id=user_id,
            workspace_id=workspace_id,
            project_id=project_id,
            research_job_id=research_job_id,
            metadata_json=metadata_json or {},
            status="draft",
        )
        self.session.add(proposal)
        await self.session.flush()
        return proposal

    async def get_proposal(self, proposal_id: uuid.UUID) -> Optional[DBGrantProposal]:
        stmt = (
            select(DBGrantProposal)
            .options(
                selectinload(DBGrantProposal.aims),
                selectinload(DBGrantProposal.budget_items),
                selectinload(DBGrantProposal.review_scorecards),
            )
            .where(DBGrantProposal.id == proposal_id)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_proposals(
        self,
        workspace_id: Optional[uuid.UUID] = None,
        funding_agency: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBGrantProposal]:
        stmt = (
            select(DBGrantProposal)
            .options(
                selectinload(DBGrantProposal.aims),
                selectinload(DBGrantProposal.budget_items),
            )
            .order_by(DBGrantProposal.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if workspace_id:
            stmt = stmt.where(DBGrantProposal.workspace_id == workspace_id)
        if funding_agency:
            stmt = stmt.where(DBGrantProposal.funding_agency == funding_agency)
        if status:
            stmt = stmt.where(DBGrantProposal.status == status)

        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def update_proposal_narratives(
        self,
        proposal_id: uuid.UUID,
        executive_abstract: Optional[str] = None,
        significance_narrative: Optional[str] = None,
        innovation_narrative: Optional[str] = None,
        approach_narrative: Optional[str] = None,
        preliminary_data_summary: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Optional[DBGrantProposal]:
        proposal = await self.get_proposal(proposal_id)
        if not proposal:
            return None

        if executive_abstract is not None:
            proposal.executive_abstract = executive_abstract
        if significance_narrative is not None:
            proposal.significance_narrative = significance_narrative
        if innovation_narrative is not None:
            proposal.innovation_narrative = innovation_narrative
        if approach_narrative is not None:
            proposal.approach_narrative = approach_narrative
        if preliminary_data_summary is not None:
            proposal.preliminary_data_summary = preliminary_data_summary
        if status is not None:
            proposal.status = status

        await self.session.flush()
        return proposal

    async def add_specific_aim(
        self,
        proposal_id: uuid.UUID,
        aim_number: int,
        title: str,
        hypothesis: str,
        experimental_design: str,
        expected_outcomes: str,
        potential_pitfalls_and_alternatives: Optional[str] = None,
        milestones_json: Optional[List[Dict[str, Any]]] = None,
        allocated_effort_percent: float = 33.3,
    ) -> DBGrantSpecificAim:
        aim = DBGrantSpecificAim(
            id=uuid.uuid4(),
            proposal_id=proposal_id,
            aim_number=aim_number,
            title=title,
            hypothesis=hypothesis,
            experimental_design=experimental_design,
            expected_outcomes=expected_outcomes,
            potential_pitfalls_and_alternatives=potential_pitfalls_and_alternatives,
            milestones_json=milestones_json or [],
            allocated_effort_percent=allocated_effort_percent,
        )
        self.session.add(aim)
        await self.session.flush()
        return aim

    async def add_budget_item(
        self,
        proposal_id: uuid.UUID,
        year_number: int,
        category: str,
        item_name: str,
        cost_usd: float,
        justification: str,
        is_direct_cost: bool = True,
    ) -> DBGrantBudgetItem:
        item = DBGrantBudgetItem(
            id=uuid.uuid4(),
            proposal_id=proposal_id,
            year_number=year_number,
            category=category,
            item_name=item_name,
            cost_usd=cost_usd,
            justification=justification,
            is_direct_cost="true" if is_direct_cost else "false",
        )
        self.session.add(item)
        await self.session.flush()
        return item

    async def record_review_scorecard(
        self,
        proposal_id: uuid.UUID,
        reviewer_persona: str,
        significance_score: float,
        investigators_score: float,
        innovation_score: float,
        approach_score: float,
        environment_score: float,
        overall_impact_score: float,
        recommendation: str,
        critique_strengths: List[str],
        critique_weaknesses: List[str],
        summary_statement: str,
    ) -> DBGrantReviewScorecard:
        scorecard = DBGrantReviewScorecard(
            id=uuid.uuid4(),
            proposal_id=proposal_id,
            reviewer_persona=reviewer_persona,
            significance_score=significance_score,
            investigators_score=investigators_score,
            innovation_score=innovation_score,
            approach_score=approach_score,
            environment_score=environment_score,
            overall_impact_score=overall_impact_score,
            recommendation=recommendation,
            critique_strengths=critique_strengths,
            critique_weaknesses=critique_weaknesses,
            summary_statement=summary_statement,
        )
        self.session.add(scorecard)

        # Update proposal average score
        proposal = await self.get_proposal(proposal_id)
        if proposal:
            proposal.mock_panel_overall_score = overall_impact_score
            proposal.percentile_estimate = max(1.0, min(99.0, (9.0 - overall_impact_score) / 8.0 * 100.0))
            proposal.status = "review_ready"

        await self.session.flush()
        return scorecard

    async def delete_proposal(self, proposal_id: uuid.UUID) -> bool:
        proposal = await self.get_proposal(proposal_id)
        if not proposal:
            return False
        await self.session.delete(proposal)
        await self.session.flush()
        return True
