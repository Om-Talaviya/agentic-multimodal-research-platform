"""
FastAPI router for Scientific Peer-Review Referee Panel (Phase 64).
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session
from database.repositories.peer_review_repo import PeerReviewRepository
from research.peer_review.peer_review_engine import ScientificPeerReviewEngine

router = APIRouter(prefix="/peer-review", tags=["Scientific Peer-Review Panel"])


class SubmitManuscriptRequest(BaseModel):
    manuscript_title: str = Field(default="Autonomous Multi-Modal AI Scientist for Closed-Loop Therapeutic Discovery")
    research_domain: str = Field(default="Computational Immuno-Oncology & Bioprocess")
    abstract_text: str = Field(default="We present an autonomous end-to-end multimodal agent platform capable of discovering neoantigens, optimizing ADC payload-linkers, and orchestrating clinical trials.")


@router.post("/manuscripts", status_code=status.HTTP_201_CREATED)
async def submit_manuscript_for_review(
    request: SubmitManuscriptRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Submits a scientific manuscript to the autonomous 3-agent referee panel with automated rebuttal generation."""
    repo = PeerReviewRepository(db)
    manuscript = await repo.create_manuscript(
        manuscript_title=request.manuscript_title,
        research_domain=request.research_domain,
        abstract_text=request.abstract_text,
    )

    eval_result = ScientificPeerReviewEngine.evaluate_manuscript(
        title=request.manuscript_title,
        abstract=request.abstract_text,
    )

    return await repo.add_reviews_and_rebuttals(
        manuscript_id=manuscript.id,
        reviews_data=eval_result["reviews"],
        overall_score=eval_result["overall_score"],
        editorial_recommendation=eval_result["editorial_recommendation"],
    )


@router.get("/manuscripts")
async def list_manuscripts(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
):
    """Lists reviewed manuscripts."""
    repo = PeerReviewRepository(db)
    return await repo.list_manuscripts(limit=limit)


@router.get("/manuscripts/{manuscript_id}")
async def get_manuscript(
    manuscript_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieves full referee reviews, statistical scores, and structured author rebuttal counter-arguments."""
    repo = PeerReviewRepository(db)
    manuscript = await repo.get_manuscript(manuscript_id)
    if not manuscript:
        raise HTTPException(status_code=404, detail="Manuscript not found")
    return manuscript
