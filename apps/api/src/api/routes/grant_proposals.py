"""FastAPI REST API routes for Autonomous Scientific Grant & Research Proposal Engine (Phase 35)."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session, get_optional_current_user
from database.repositories.grant_proposal_repo import GrantProposalRepository
from research.grants.synthesizer import GrantProposalSynthesizer, InstitutionalBudgetCalculator
from shared.auth import User

router = APIRouter(prefix="/grants", tags=["grant-proposals"])
synthesizer = GrantProposalSynthesizer()
budget_calculator = InstitutionalBudgetCalculator()


class CreateGrantProposalRequest(BaseModel):
    title: str = Field(..., description="Title of the research grant proposal")
    funding_agency: str = Field("NIH", description="NIH, NSF, HORIZON_EUROPE, DARPA, DOE")
    grant_mechanism: str = Field("R01", description="R01, R21, CAREER, ERC_ADVANCED, BAA")
    target_call_number: Optional[str] = None
    project_duration_years: int = Field(5, ge=1, le=7)
    total_requested_budget_usd: float = Field(1500000.0, ge=10000.0)
    indirect_cost_rate_percent: float = Field(52.0, ge=0.0, le=100.0)
    workspace_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    research_job_id: Optional[uuid.UUID] = None


class SynthesizeProposalRequest(BaseModel):
    research_topic: str = Field(..., description="Target scientific research topic")
    key_findings: Optional[List[str]] = Field(default_factory=list)


class CalculateBudgetRequest(BaseModel):
    duration_years: int = 5
    pi_base_salary: float = 180000.0
    pi_effort_months: float = 2.0
    postdoc_count: int = 1
    postdoc_base_salary: float = 65000.0
    grad_student_count: int = 2
    grad_student_stipend: float = 38000.0
    equipment_cost_y1: float = 120000.0
    cloud_compute_annual: float = 45000.0
    supplies_annual: float = 25000.0
    travel_annual: float = 10000.0
    fringe_rate_percent: float = 28.5
    indirect_rate_percent: float = 52.0
    annual_escalation_percent: float = 3.0


@router.post("/proposals", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_grant_proposal(
    payload: CreateGrantProposalRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Create a new scientific grant proposal project."""
    repo = GrantProposalRepository(session)
    user_uuid = uuid.UUID(current_user.id) if (current_user and current_user.id) else None

    proposal = await repo.create_proposal(
        title=payload.title,
        funding_agency=payload.funding_agency,
        grant_mechanism=payload.grant_mechanism,
        target_call_number=payload.target_call_number,
        project_duration_years=payload.project_duration_years,
        total_requested_budget_usd=payload.total_requested_budget_usd,
        indirect_cost_rate_percent=payload.indirect_cost_rate_percent,
        user_id=user_uuid,
        workspace_id=payload.workspace_id,
        project_id=payload.project_id,
        research_job_id=payload.research_job_id,
    )
    return proposal.to_dict()


@router.get("/proposals", response_model=List[Dict[str, Any]])
async def list_grant_proposals(
    workspace_id: Optional[uuid.UUID] = Query(None),
    funding_agency: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session),
):
    """List grant proposals filtered by agency, workspace, or status."""
    repo = GrantProposalRepository(session)
    proposals = await repo.list_proposals(
        workspace_id=workspace_id,
        funding_agency=funding_agency,
        status=status,
        limit=limit,
        offset=offset,
    )
    return [p.to_dict() for p in proposals]


@router.get("/proposals/{id}", response_model=Dict[str, Any])
async def get_grant_proposal(
    id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Retrieve full grant proposal details with specific aims and budget."""
    repo = GrantProposalRepository(session)
    proposal = await repo.get_proposal(id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Grant proposal not found")

    res = proposal.to_dict()
    res["aims"] = [aim.to_dict() for aim in (proposal.aims or [])]
    res["budget_items"] = [b.to_dict() for b in (proposal.budget_items or [])]
    res["review_scorecards"] = [r.to_dict() for r in (proposal.review_scorecards or [])]
    return res


@router.post("/proposals/{id}/synthesize", response_model=Dict[str, Any])
async def synthesize_proposal(
    id: uuid.UUID,
    payload: SynthesizeProposalRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Synthesizes Specific Aims, Significance, Innovation, and Approach narratives."""
    repo = GrantProposalRepository(session)
    proposal = await repo.get_proposal(id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Grant proposal not found")

    synth_res = synthesizer.synthesize_proposal_narratives(
        title=proposal.title,
        research_topic=payload.research_topic,
        funding_agency=proposal.funding_agency,
        grant_mechanism=proposal.grant_mechanism,
        key_findings=payload.key_findings,
    )

    await repo.update_proposal_narratives(
        proposal_id=id,
        executive_abstract=synth_res["executive_abstract"],
        significance_narrative=synth_res["significance_narrative"],
        innovation_narrative=synth_res["innovation_narrative"],
        approach_narrative=synth_res["approach_narrative"],
        preliminary_data_summary=synth_res["preliminary_data_summary"],
        status="synthesized",
    )

    # Add synthesized aims
    for aim_data in synth_res.get("specific_aims", []):
        await repo.add_specific_aim(
            proposal_id=id,
            aim_number=aim_data["aim_number"],
            title=aim_data["title"],
            hypothesis=aim_data["hypothesis"],
            experimental_design=aim_data["experimental_design"],
            expected_outcomes=aim_data["expected_outcomes"],
            potential_pitfalls_and_alternatives=aim_data["potential_pitfalls_and_alternatives"],
            milestones_json=aim_data["milestones"],
            allocated_effort_percent=aim_data["allocated_effort_percent"],
        )

    return await get_grant_proposal(id, session)


@router.post("/proposals/{id}/budget/calculate", response_model=Dict[str, Any])
async def calculate_proposal_budget(
    id: uuid.UUID,
    payload: CalculateBudgetRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Calculates granular institutional budget with MTDC, Fringe, and F&A Indirects."""
    repo = GrantProposalRepository(session)
    proposal = await repo.get_proposal(id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Grant proposal not found")

    budget_result = budget_calculator.calculate_multiyear_budget(
        duration_years=payload.duration_years,
        pi_base_salary=payload.pi_base_salary,
        pi_effort_months=payload.pi_effort_months,
        postdoc_count=payload.postdoc_count,
        postdoc_base_salary=payload.postdoc_base_salary,
        grad_student_count=payload.grad_student_count,
        grad_student_stipend=payload.grad_student_stipend,
        equipment_cost_y1=payload.equipment_cost_y1,
        cloud_compute_annual=payload.cloud_compute_annual,
        supplies_annual=payload.supplies_annual,
        travel_annual=payload.travel_annual,
        fringe_rate_percent=payload.fringe_rate_percent,
        indirect_rate_percent=payload.indirect_rate_percent,
        annual_escalation_percent=payload.annual_escalation_percent,
    )

    # Record budget items in database
    for y_data in budget_result["yearly_breakdowns"]:
        y_num = y_data["year"]
        await repo.add_budget_item(
            proposal_id=id,
            year_number=y_num,
            category="personnel",
            item_name=f"Year {y_num} Personnel (PI, Postdoc, Grads)",
            cost_usd=y_data["personnel_salaries"],
            justification=f"Covers PI effort and student researcher support in Year {y_num}.",
            is_direct_cost=True,
        )
        await repo.add_budget_item(
            proposal_id=id,
            year_number=y_num,
            category="compute_cloud",
            item_name=f"Year {y_num} Cloud GPU & Storage",
            cost_usd=y_data["cloud_compute"],
            justification="H100/A100 GPU compute allocations and high-throughput vector store hosting.",
            is_direct_cost=True,
        )

    return budget_result


@router.post("/proposals/{id}/score-mock-panel", response_model=Dict[str, Any])
async def score_mock_study_section(
    id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Simulates an NIH/NSF study section peer review panel evaluation."""
    repo = GrantProposalRepository(session)
    proposal = await repo.get_proposal(id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Grant proposal not found")

    mock_review = synthesizer.conduct_mock_study_section_review(
        proposal_title=proposal.title,
        aims_count=len(proposal.aims) if proposal.aims else 3,
        total_budget=proposal.total_requested_budget_usd,
    )

    scorecard = await repo.record_review_scorecard(
        proposal_id=id,
        reviewer_persona=mock_review["reviewer_persona"],
        significance_score=mock_review["significance_score"],
        investigators_score=mock_review["investigators_score"],
        innovation_score=mock_review["innovation_score"],
        approach_score=mock_review["approach_score"],
        environment_score=mock_review["environment_score"],
        overall_impact_score=mock_review["overall_impact_score"],
        recommendation=mock_review["recommendation"],
        critique_strengths=mock_review["critique_strengths"],
        critique_weaknesses=mock_review["critique_weaknesses"],
        summary_statement=mock_review["summary_statement"],
    )

    return scorecard.to_dict()


@router.get("/proposals/{id}/export-latex", response_model=Dict[str, Any])
async def export_proposal_latex(
    id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Exports proposal into compilable LaTeX grant formatting."""
    repo = GrantProposalRepository(session)
    proposal = await repo.get_proposal(id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Grant proposal not found")

    latex_code = synthesizer.export_proposal_latex(
        proposal=proposal.to_dict(),
        budget_data={"total_requested_budget": proposal.total_requested_budget_usd, "duration_years": proposal.project_duration_years, "indirect_rate_percent": proposal.indirect_cost_rate_percent}
    )

    return {
        "proposal_id": str(id),
        "latex_content": latex_code,
    }
