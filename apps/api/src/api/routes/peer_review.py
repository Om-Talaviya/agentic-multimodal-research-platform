"""REST API routes for Autonomous Peer Review and Scientific Publishing Pipeline."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db_session
from database.models.peer_review import (
    DBManuscriptRevision,
    DBPeerReviewManuscript,
    DBPeerReviewReport,
)
from database.repositories.peer_review_repo import PeerReviewRepository
from research.publishing.peer_review import (
    AuthorRebuttalGenerator,
    PeerReviewEngine,
    PublicationFormatter,
)
from shared.auth import User
from shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/publishing", tags=["publishing"])


# ---------------- Request & Response Schemas ----------------

class SubmitManuscriptPayload(BaseModel):
    title: str = Field(..., min_length=5, max_length=512)
    abstract: str = Field(..., min_length=20)
    field_of_study: str = Field(default="computer_science")
    venue_format: str = Field(default="nature", pattern="^(nature|ieee|acm|arxiv)$")
    manuscript_content: Optional[str] = None
    claimed_contributions: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    workspace_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    research_job_id: Optional[uuid.UUID] = None


class SubmitRevisionPayload(BaseModel):
    rebuttal_letter: Optional[str] = None
    diff_summary: Optional[str] = None
    auto_generate_rebuttal: bool = Field(default=False)


class PublishManuscriptPayload(BaseModel):
    authors: List[str] = Field(default_factory=lambda: ["Om Talaviya", "Agentic Multimodal Research Systems"])
    publication_year: int = Field(default=2026)


# ---------------- Route Implementations ----------------

@router.post("/manuscripts", status_code=status.HTTP_201_CREATED)
async def submit_manuscript(
    payload: SubmitManuscriptPayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Submit a research paper manuscript for multi-agent peer review."""
    repo = PeerReviewRepository(session)
    manuscript = DBPeerReviewManuscript(
        user_id=current_user.id,
        workspace_id=payload.workspace_id,
        project_id=payload.project_id,
        research_job_id=payload.research_job_id,
        title=payload.title,
        abstract=payload.abstract,
        field_of_study=payload.field_of_study,
        venue_format=payload.venue_format,
        manuscript_content=payload.manuscript_content,
        claimed_contributions=payload.claimed_contributions,
        keywords=payload.keywords,
        status="submitted",
    )
    created = await repo.create_manuscript(manuscript)
    return {
        "id": str(created.id),
        "title": created.title,
        "abstract": created.abstract,
        "field_of_study": created.field_of_study,
        "venue_format": created.venue_format,
        "status": created.status,
        "overall_score": created.overall_score,
        "created_at": created.created_at.isoformat(),
    }


@router.get("/metrics")
async def get_peer_review_platform_metrics(
    workspace_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Query aggregate peer review, referee scorecard, and publication metrics."""
    repo = PeerReviewRepository(session)
    return await repo.get_peer_review_metrics(workspace_id=workspace_id)


@router.get("/manuscripts")
async def list_manuscripts(
    workspace_id: Optional[uuid.UUID] = Query(None),
    project_id: Optional[uuid.UUID] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    venue_format: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """List submitted manuscripts with status and score metrics."""
    repo = PeerReviewRepository(session)
    manuscripts = await repo.list_manuscripts(
        user_id=current_user.id if not workspace_id else None,
        workspace_id=workspace_id,
        project_id=project_id,
        status=status_filter,
        venue_format=venue_format,
        limit=limit,
        offset=offset,
    )
    return [
        {
            "id": str(m.id),
            "title": m.title,
            "abstract": m.abstract,
            "field_of_study": m.field_of_study,
            "venue_format": m.venue_format,
            "status": m.status,
            "overall_score": m.overall_score,
            "camera_ready_doi": m.camera_ready_doi,
            "created_at": m.created_at.isoformat(),
        }
        for m in manuscripts
    ]


@router.get("/manuscripts/{manuscript_id}")
async def get_manuscript(
    manuscript_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Fetch complete manuscript dossier with referee reports and author revisions."""
    repo = PeerReviewRepository(session)
    m = await repo.get_manuscript(manuscript_id)
    if not m:
        raise HTTPException(status_code=404, detail="Manuscript not found")

    return {
        "id": str(m.id),
        "title": m.title,
        "abstract": m.abstract,
        "field_of_study": m.field_of_study,
        "venue_format": m.venue_format,
        "status": m.status,
        "manuscript_content": m.manuscript_content,
        "claimed_contributions": m.claimed_contributions,
        "keywords": m.keywords,
        "overall_score": m.overall_score,
        "camera_ready_doi": m.camera_ready_doi,
        "published_latex": m.published_latex,
        "bibtex_citation": m.bibtex_citation,
        "created_at": m.created_at.isoformat(),
        "reports": [
            {
                "id": str(r.id),
                "reviewer_persona": r.reviewer_persona,
                "reviewer_title": r.reviewer_title,
                "originality_score": r.originality_score,
                "methodology_score": r.methodology_score,
                "empirical_soundness": r.empirical_soundness,
                "clarity_score": r.clarity_score,
                "composite_score": r.composite_score,
                "recommendation": r.recommendation,
                "summary_verdict": r.summary_verdict,
                "strengths": r.strengths,
                "weaknesses": r.weaknesses,
                "detailed_critique": r.detailed_critique,
                "required_revisions": r.required_revisions,
                "created_at": r.created_at.isoformat(),
            }
            for r in m.reports
        ],
        "revisions": [
            {
                "id": str(rev.id),
                "revision_round": rev.revision_round,
                "rebuttal_letter": rev.rebuttal_letter,
                "diff_summary": rev.diff_summary,
                "point_by_point_responses": rev.point_by_point_responses,
                "status": rev.status,
                "created_at": rev.created_at.isoformat(),
            }
            for rev in m.revisions
        ],
    }


@router.post("/manuscripts/{manuscript_id}/review", status_code=status.HTTP_200_OK)
async def trigger_peer_review_evaluation(
    manuscript_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Execute multi-agent double-blind peer review evaluation."""
    repo = PeerReviewRepository(session)
    manuscript = await repo.get_manuscript(manuscript_id)
    if not manuscript:
        raise HTTPException(status_code=404, detail="Manuscript not found")

    review_result = PeerReviewEngine.evaluate_manuscript(
        title=manuscript.title,
        abstract=manuscript.abstract,
        content=manuscript.manuscript_content,
        field_of_study=manuscript.field_of_study,
        claimed_contributions=manuscript.claimed_contributions,
        venue_format=manuscript.venue_format,
    )

    db_reports = [
        DBPeerReviewReport(
            reviewer_persona=rep["reviewer_persona"],
            reviewer_title=rep["reviewer_title"],
            originality_score=rep["originality_score"],
            methodology_score=rep["methodology_score"],
            empirical_soundness=rep["empirical_soundness"],
            clarity_score=rep["clarity_score"],
            composite_score=rep["composite_score"],
            recommendation=rep["recommendation"],
            summary_verdict=rep["summary_verdict"],
            strengths=rep["strengths"],
            weaknesses=rep["weaknesses"],
            detailed_critique=rep["detailed_critique"],
            required_revisions=rep["required_revisions"],
        )
        for rep in review_result["referee_reports"]
    ]

    saved_reports = await repo.save_peer_review_reports(manuscript_id, db_reports)
    updated_m = await repo.get_manuscript(manuscript_id)

    return {
        "manuscript_id": str(manuscript_id),
        "editorial_decision": updated_m.status if updated_m else review_result["editorial_decision"],
        "overall_score": updated_m.overall_score if updated_m else review_result["average_composite_score"],
        "referee_reports_count": len(saved_reports),
        "reports": [
            {
                "id": str(r.id),
                "reviewer_persona": r.reviewer_persona,
                "composite_score": r.composite_score,
                "recommendation": r.recommendation,
                "summary_verdict": r.summary_verdict,
            }
            for r in saved_reports
        ],
    }


@router.post("/manuscripts/{manuscript_id}/revisions", status_code=status.HTTP_201_CREATED)
async def submit_manuscript_revision(
    manuscript_id: uuid.UUID,
    payload: SubmitRevisionPayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Submit author rebuttal and revision round against referee critiques."""
    repo = PeerReviewRepository(session)
    manuscript = await repo.get_manuscript(manuscript_id)
    if not manuscript:
        raise HTTPException(status_code=404, detail="Manuscript not found")

    next_round = len(manuscript.revisions) + 1

    if payload.auto_generate_rebuttal or not payload.rebuttal_letter:
        reports_dict = [
            {
                "reviewer_persona": r.reviewer_persona,
                "reviewer_title": r.reviewer_title,
                "required_revisions": r.required_revisions,
                "weaknesses": r.weaknesses,
            }
            for r in manuscript.reports
        ]
        rebuttal_data = AuthorRebuttalGenerator.generate_rebuttal(
            manuscript_title=manuscript.title,
            reports=reports_dict,
            revision_round=next_round,
        )
        rebuttal_letter = rebuttal_data["rebuttal_letter"]
        point_by_point = rebuttal_data["point_by_point_responses"]
        diff_summary = payload.diff_summary or rebuttal_data["diff_summary"]
    else:
        rebuttal_letter = payload.rebuttal_letter
        point_by_point = []
        diff_summary = payload.diff_summary or f"Author revision round {next_round}"

    revision = DBManuscriptRevision(
        manuscript_id=manuscript_id,
        revision_round=next_round,
        rebuttal_letter=rebuttal_letter,
        diff_summary=diff_summary,
        point_by_point_responses=point_by_point,
        status="submitted",
    )

    created_rev = await repo.add_manuscript_revision(revision)
    return {
        "id": str(created_rev.id),
        "manuscript_id": str(manuscript_id),
        "revision_round": created_rev.revision_round,
        "rebuttal_letter": created_rev.rebuttal_letter,
        "diff_summary": created_rev.diff_summary,
        "point_by_point_responses": created_rev.point_by_point_responses,
        "status": created_rev.status,
    }


@router.post("/manuscripts/{manuscript_id}/publish", status_code=status.HTTP_200_OK)
async def publish_accepted_manuscript(
    manuscript_id: uuid.UUID,
    payload: PublishManuscriptPayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Generate camera-ready LaTeX preprint, BibTeX entry, and formal DOI."""
    repo = PeerReviewRepository(session)
    manuscript = await repo.get_manuscript(manuscript_id)
    if not manuscript:
        raise HTTPException(status_code=404, detail="Manuscript not found")

    doi = PublicationFormatter.generate_doi(manuscript.title, venue_format=manuscript.venue_format)
    bibtex = PublicationFormatter.generate_bibtex(
        title=manuscript.title,
        authors=payload.authors,
        year=payload.publication_year,
        doi=doi,
        venue_format=manuscript.venue_format,
    )
    latex = PublicationFormatter.generate_latex_source(
        title=manuscript.title,
        abstract=manuscript.abstract,
        authors=payload.authors,
        content=manuscript.manuscript_content,
        keywords=manuscript.keywords,
        doi=doi,
        venue_format=manuscript.venue_format,
    )

    published = await repo.publish_manuscript(
        manuscript_id=manuscript_id,
        doi=doi,
        latex=latex,
        bibtex=bibtex,
    )

    return {
        "id": str(manuscript_id),
        "status": "published",
        "camera_ready_doi": doi,
        "bibtex_citation": bibtex,
        "published_latex_preview": latex[:300] + "...",
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


@router.delete("/manuscripts/{manuscript_id}", status_code=status.HTTP_200_OK)
async def delete_manuscript(
    manuscript_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Delete manuscript and all associated referee reports and revisions."""
    repo = PeerReviewRepository(session)
    deleted = await repo.delete_manuscript(manuscript_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Manuscript not found")
    return {"message": "Manuscript deleted", "id": str(manuscript_id)}
