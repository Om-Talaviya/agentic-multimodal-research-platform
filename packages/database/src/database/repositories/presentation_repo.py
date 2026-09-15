"""Repository for Multimodal Scientific Presentations, Slides, and Podcast Briefings persistence."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.presentation import (
    DBPodcastBriefing,
    DBPresentationSlide,
    DBSynthesisPresentation,
)
from shared.logging import get_logger

logger = get_logger(__name__)


class PresentationRepository:
    """Async repository for managing presentation slide decks and audio podcast briefings."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ---------------- Presentation Deck Operations ----------------

    async def create_presentation(
        self,
        user_id: uuid.UUID,
        title: str,
        subtitle: Optional[str] = None,
        target_audience: str = "executive",
        theme: str = "midnight_slate",
        estimated_duration_min: int = 15,
        research_job_id: Optional[uuid.UUID] = None,
        workspace_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        metadata_json: Optional[Dict[str, Any]] = None,
    ) -> DBSynthesisPresentation:
        """Create a new presentation slide deck entity."""
        pres = DBSynthesisPresentation(
            id=uuid.uuid4(),
            user_id=user_id,
            research_job_id=research_job_id,
            workspace_id=workspace_id,
            project_id=project_id,
            title=title,
            subtitle=subtitle,
            target_audience=target_audience,
            theme=theme,
            estimated_duration_min=estimated_duration_min,
            total_slides=0,
            metadata_json=metadata_json or {},
        )
        self.session.add(pres)
        await self.session.commit()
        await self.session.refresh(pres)
        logger.info("presentation_created", presentation_id=str(pres.id), title=title)
        return pres

    async def get_presentation(
        self,
        presentation_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        include_slides: bool = True,
    ) -> Optional[DBSynthesisPresentation]:
        """Fetch presentation deck by ID with eager loaded slides."""
        stmt = select(DBSynthesisPresentation).where(DBSynthesisPresentation.id == presentation_id)
        if user_id:
            stmt = stmt.where(DBSynthesisPresentation.user_id == user_id)

        if include_slides:
            stmt = stmt.options(selectinload(DBSynthesisPresentation.slides))

        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_presentations(
        self,
        user_id: Optional[uuid.UUID] = None,
        workspace_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        target_audience: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBSynthesisPresentation]:
        """List presentations with filtering."""
        stmt = (
            select(DBSynthesisPresentation)
            .options(selectinload(DBSynthesisPresentation.slides))
            .order_by(DBSynthesisPresentation.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if user_id:
            stmt = stmt.where(DBSynthesisPresentation.user_id == user_id)
        if workspace_id:
            stmt = stmt.where(DBSynthesisPresentation.workspace_id == workspace_id)
        if project_id:
            stmt = stmt.where(DBSynthesisPresentation.project_id == project_id)
        if target_audience:
            stmt = stmt.where(DBSynthesisPresentation.target_audience == target_audience)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_presentation_slides_batch(
        self,
        presentation_id: uuid.UUID,
        slides_data: List[Dict[str, Any]],
    ) -> List[DBPresentationSlide]:
        """Batch insert slides into a presentation."""
        created_slides = []
        for idx, s in enumerate(slides_data, start=1):
            slide = DBPresentationSlide(
                id=uuid.uuid4(),
                presentation_id=presentation_id,
                slide_number=s.get("slide_number", idx),
                layout_type=s.get("layout_type", "bullet_points"),
                headline=s.get("headline", "Key Insight"),
                bullet_points=s.get("bullet_points", []),
                speaker_notes=s.get("speaker_notes"),
                visual_metadata=s.get("visual_metadata", {}),
            )
            self.session.add(slide)
            created_slides.append(slide)

        await self.session.commit()

        # Update total slide count on parent
        await self.session.execute(
            update(DBSynthesisPresentation)
            .where(DBSynthesisPresentation.id == presentation_id)
            .values(total_slides=len(created_slides), updated_at=datetime.now(timezone.utc))
        )
        await self.session.commit()

        for sl in created_slides:
            await self.session.refresh(sl)
        return created_slides

    async def delete_presentation(self, presentation_id: uuid.UUID) -> bool:
        """Delete presentation and cascade slides."""
        stmt = delete(DBSynthesisPresentation).where(DBSynthesisPresentation.id == presentation_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return (result.rowcount or 0) > 0

    # ---------------- Podcast Audio Briefing Operations ----------------

    async def create_podcast_briefing(
        self,
        user_id: uuid.UUID,
        title: str,
        episode_topic: str,
        host_name: str = "Dr. Elena Vance (Host)",
        expert_name: str = "Prof. Marcus Sterling (Specialist)",
        total_duration_sec: float = 180.0,
        dialogue_transcript_json: Optional[List[Dict[str, Any]]] = None,
        audio_url: Optional[str] = None,
        research_job_id: Optional[uuid.UUID] = None,
        workspace_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
    ) -> DBPodcastBriefing:
        """Create a multi-speaker scientific audio briefing record."""
        turns = dialogue_transcript_json or []
        podcast = DBPodcastBriefing(
            id=uuid.uuid4(),
            user_id=user_id,
            research_job_id=research_job_id,
            workspace_id=workspace_id,
            project_id=project_id,
            title=title,
            episode_topic=episode_topic,
            host_name=host_name,
            expert_name=expert_name,
            total_duration_sec=total_duration_sec,
            total_dialogue_turns=len(turns),
            dialogue_transcript_json=turns,
            audio_url=audio_url,
            status="synthesized",
        )
        self.session.add(podcast)
        await self.session.commit()
        await self.session.refresh(podcast)
        logger.info("podcast_briefing_created", podcast_id=str(podcast.id), title=title)
        return podcast

    async def get_podcast_briefing(self, podcast_id: uuid.UUID) -> Optional[DBPodcastBriefing]:
        """Fetch podcast briefing by ID."""
        stmt = select(DBPodcastBriefing).where(DBPodcastBriefing.id == podcast_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_podcast_briefings(
        self,
        user_id: Optional[uuid.UUID] = None,
        workspace_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBPodcastBriefing]:
        """Query podcast briefings."""
        stmt = select(DBPodcastBriefing).order_by(DBPodcastBriefing.created_at.desc()).limit(limit).offset(offset)
        if user_id:
            stmt = stmt.where(DBPodcastBriefing.user_id == user_id)
        if workspace_id:
            stmt = stmt.where(DBPodcastBriefing.workspace_id == workspace_id)
        if project_id:
            stmt = stmt.where(DBPodcastBriefing.project_id == project_id)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_podcast_briefing(self, podcast_id: uuid.UUID) -> bool:
        """Delete podcast briefing."""
        stmt = delete(DBPodcastBriefing).where(DBPodcastBriefing.id == podcast_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return (result.rowcount or 0) > 0

    # ---------------- Aggregate Platform Metrics ----------------

    async def get_presentation_metrics(self) -> Dict[str, Any]:
        """Query presentation and podcast statistics."""
        total_presentations = await self.session.scalar(select(func.count(DBSynthesisPresentation.id))) or 0
        total_slides = await self.session.scalar(select(func.count(DBPresentationSlide.id))) or 0
        total_podcasts = await self.session.scalar(select(func.count(DBPodcastBriefing.id))) or 0
        total_audio_seconds = await self.session.scalar(select(func.sum(DBPodcastBriefing.total_duration_sec))) or 0.0

        return {
            "total_presentations": total_presentations,
            "total_slides": total_slides,
            "average_slides_per_deck": round(total_slides / max(1, total_presentations), 1),
            "total_podcasts": total_podcasts,
            "total_audio_minutes": round(float(total_audio_seconds) / 60.0, 1),
        }
