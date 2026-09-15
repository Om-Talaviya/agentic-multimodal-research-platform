"""REST API endpoints for Multimodal Presentations and Multi-Speaker Scientific Podcasts."""

from typing import Any, Dict, List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db_session
from database.models.user import User
from database.repositories.presentation_repo import PresentationRepository
from research.presentation.synthesizer import (
    PresentationGenerator,
    PodcastBriefingSynthesizer,
)
from shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/presentations", tags=["Presentations & Podcasts"])


# ---------------- Schemas ----------------

class GeneratePresentationPayload(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    research_content: str = Field(..., min_length=10)
    subtitle: Optional[str] = None
    target_audience: str = Field(default="executive", pattern="^(executive|scientific|technical|general)$")
    theme: str = Field(default="midnight_slate")
    research_job_id: Optional[uuid.UUID] = None
    workspace_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None


class GeneratePodcastPayload(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500)
    key_findings: str = Field(..., min_length=10)
    host_name: str = Field(default="Dr. Elena Vance (Host)")
    expert_name: str = Field(default="Prof. Marcus Sterling (Specialist)")
    research_job_id: Optional[uuid.UUID] = None
    workspace_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None


# ---------------- Presentation Endpoints ----------------

@router.post("", status_code=status.HTTP_201_CREATED)
async def generate_presentation(
    payload: GeneratePresentationPayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Synthesize a complete scientific presentation deck with slides and speaker notes."""
    repo = PresentationRepository(session)

    deck = PresentationGenerator.generate_deck_from_research(
        title=payload.title,
        research_content=payload.research_content,
        target_audience=payload.target_audience,
        theme=payload.theme,
        subtitle=payload.subtitle,
    )

    pres = await repo.create_presentation(
        user_id=current_user.id,
        title=deck["title"],
        subtitle=deck["subtitle"],
        target_audience=deck["target_audience"],
        theme=deck["theme"],
        estimated_duration_min=deck["estimated_duration_min"],
        research_job_id=payload.research_job_id,
        workspace_id=payload.workspace_id,
        project_id=payload.project_id,
    )

    slides = await repo.add_presentation_slides_batch(pres.id, deck["slides"])

    return {
        "id": str(pres.id),
        "title": pres.title,
        "subtitle": pres.subtitle,
        "target_audience": pres.target_audience,
        "theme": pres.theme,
        "estimated_duration_min": pres.estimated_duration_min,
        "total_slides": len(slides),
        "created_at": pres.created_at.isoformat(),
        "slides": [
            {
                "id": str(s.id),
                "slide_number": s.slide_number,
                "layout_type": s.layout_type,
                "headline": s.headline,
                "bullet_points": s.bullet_points,
                "speaker_notes": s.speaker_notes,
                "visual_metadata": s.visual_metadata,
            }
            for s in slides
        ],
    }


@router.get("")
async def list_presentations(
    workspace_id: Optional[uuid.UUID] = Query(None),
    project_id: Optional[uuid.UUID] = Query(None),
    target_audience: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """List presentation decks."""
    repo = PresentationRepository(session)
    presentations = await repo.list_presentations(
        user_id=current_user.id if not workspace_id else None,
        workspace_id=workspace_id,
        project_id=project_id,
        target_audience=target_audience,
        limit=limit,
        offset=offset,
    )
    return [
        {
            "id": str(p.id),
            "title": p.title,
            "subtitle": p.subtitle,
            "target_audience": p.target_audience,
            "theme": p.theme,
            "estimated_duration_min": p.estimated_duration_min,
            "total_slides": p.total_slides,
            "created_at": p.created_at.isoformat(),
        }
        for p in presentations
    ]


@router.get("/metrics")
async def get_presentation_platform_metrics(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Query aggregate presentation and podcast platform KPIs."""
    repo = PresentationRepository(session)
    return await repo.get_presentation_metrics()


@router.get("/{presentation_id}")
async def get_presentation(
    presentation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Fetch complete presentation deck with slides and speaker notes."""
    repo = PresentationRepository(session)
    pres = await repo.get_presentation(presentation_id)
    if not pres:
        raise HTTPException(status_code=404, detail="Presentation deck not found")

    return {
        "id": str(pres.id),
        "title": pres.title,
        "subtitle": pres.subtitle,
        "target_audience": pres.target_audience,
        "theme": pres.theme,
        "estimated_duration_min": pres.estimated_duration_min,
        "total_slides": pres.total_slides,
        "created_at": pres.created_at.isoformat(),
        "slides": [
            {
                "id": str(s.id),
                "slide_number": s.slide_number,
                "layout_type": s.layout_type,
                "headline": s.headline,
                "bullet_points": s.bullet_points,
                "speaker_notes": s.speaker_notes,
                "visual_metadata": s.visual_metadata,
            }
            for s in pres.slides
        ],
    }


@router.delete("/{presentation_id}", status_code=status.HTTP_200_OK)
async def delete_presentation(
    presentation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Delete a presentation slide deck."""
    repo = PresentationRepository(session)
    deleted = await repo.delete_presentation(presentation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Presentation deck not found")
    return {"message": "Presentation deleted", "id": str(presentation_id)}


# ---------------- Podcast Briefing Endpoints ----------------

@router.post("/podcasts", status_code=status.HTTP_201_CREATED)
async def generate_podcast_briefing(
    payload: GeneratePodcastPayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Synthesize a multi-speaker scientific audio podcast briefing."""
    repo = PresentationRepository(session)

    podcast_data = PodcastBriefingSynthesizer.generate_podcast_dialogue(
        topic=payload.topic,
        key_findings=payload.key_findings,
        host_name=payload.host_name,
        expert_name=payload.expert_name,
    )

    podcast = await repo.create_podcast_briefing(
        user_id=current_user.id,
        title=podcast_data["title"],
        episode_topic=podcast_data["episode_topic"],
        host_name=podcast_data["host_name"],
        expert_name=podcast_data["expert_name"],
        total_duration_sec=podcast_data["total_duration_sec"],
        dialogue_transcript_json=podcast_data["dialogue_transcript_json"],
        research_job_id=payload.research_job_id,
        workspace_id=payload.workspace_id,
        project_id=payload.project_id,
    )

    return {
        "id": str(podcast.id),
        "title": podcast.title,
        "episode_topic": podcast.episode_topic,
        "host_name": podcast.host_name,
        "expert_name": podcast.expert_name,
        "total_duration_sec": podcast.total_duration_sec,
        "total_dialogue_turns": podcast.total_dialogue_turns,
        "dialogue_transcript_json": podcast.dialogue_transcript_json,
        "status": podcast.status,
        "created_at": podcast.created_at.isoformat(),
    }


@router.get("/podcasts")
async def list_podcast_briefings(
    workspace_id: Optional[uuid.UUID] = Query(None),
    project_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """List podcast audio briefings."""
    repo = PresentationRepository(session)
    podcasts = await repo.list_podcast_briefings(
        user_id=current_user.id if not workspace_id else None,
        workspace_id=workspace_id,
        project_id=project_id,
        limit=limit,
        offset=offset,
    )
    return [
        {
            "id": str(p.id),
            "title": p.title,
            "episode_topic": p.episode_topic,
            "host_name": p.host_name,
            "expert_name": p.expert_name,
            "total_duration_sec": p.total_duration_sec,
            "total_dialogue_turns": p.total_dialogue_turns,
            "status": p.status,
            "created_at": p.created_at.isoformat(),
        }
        for p in podcasts
    ]


@router.get("/podcasts/{podcast_id}")
async def get_podcast_briefing(
    podcast_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Fetch podcast audio briefing details and full dialogue transcript."""
    repo = PresentationRepository(session)
    podcast = await repo.get_podcast_briefing(podcast_id)
    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast briefing not found")

    return {
        "id": str(podcast.id),
        "title": podcast.title,
        "episode_topic": podcast.episode_topic,
        "host_name": podcast.host_name,
        "expert_name": podcast.expert_name,
        "total_duration_sec": podcast.total_duration_sec,
        "total_dialogue_turns": podcast.total_dialogue_turns,
        "dialogue_transcript_json": podcast.dialogue_transcript_json,
        "audio_url": podcast.audio_url,
        "status": podcast.status,
        "created_at": podcast.created_at.isoformat(),
    }


@router.delete("/podcasts/{podcast_id}", status_code=status.HTTP_200_OK)
async def delete_podcast_briefing(
    podcast_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Delete a podcast audio briefing."""
    repo = PresentationRepository(session)
    deleted = await repo.delete_podcast_briefing(podcast_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Podcast briefing not found")
    return {"message": "Podcast briefing deleted", "id": str(podcast_id)}
