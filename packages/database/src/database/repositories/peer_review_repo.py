"""Repository for Peer Review Manuscripts, Referee Reports, and Revisions."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import delete, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.peer_review import (
    DBManuscriptRevision,
    DBPeerReviewManuscript,
    DBPeerReviewReport,
)
from shared.logging import get_logger

logger = get_logger(__name__)


class PeerReviewRepository:
    """Async database repository for academic peer review and publication workflows."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_manuscript(self, manuscript: DBPeerReviewManuscript) -> DBPeerReviewManuscript:
        """Register a new research manuscript for peer review."""
        self.session.add(manuscript)
        await self.session.commit()
        await self.session.refresh(manuscript)
        logger.info(
            "Created peer review manuscript",
            manuscript_id=str(manuscript.id),
            title=manuscript.title,
            venue_format=manuscript.venue_format,
        )
        return manuscript

    async def get_manuscript(self, manuscript_id: uuid.UUID) -> Optional[DBPeerReviewManuscript]:
        """Fetch manuscript by ID with loaded review reports and revision rounds."""
        stmt = (
            select(DBPeerReviewManuscript)
            .options(
                selectinload(DBPeerReviewManuscript.reports),
                selectinload(DBPeerReviewManuscript.revisions),
            )
            .where(DBPeerReviewManuscript.id == manuscript_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_manuscripts(
        self,
        user_id: Optional[uuid.UUID] = None,
        workspace_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        venue_format: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBPeerReviewManuscript]:
        """List manuscripts matching optional filter criteria."""
        stmt = select(DBPeerReviewManuscript).order_by(desc(DBPeerReviewManuscript.created_at))

        if user_id:
            stmt = stmt.where(DBPeerReviewManuscript.user_id == user_id)
        if workspace_id:
            stmt = stmt.where(DBPeerReviewManuscript.workspace_id == workspace_id)
        if project_id:
            stmt = stmt.where(DBPeerReviewManuscript.project_id == project_id)
        if status:
            stmt = stmt.where(DBPeerReviewManuscript.status == status)
        if venue_format:
            stmt = stmt.where(DBPeerReviewManuscript.venue_format == venue_format)

        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_manuscript_status(
        self,
        manuscript_id: uuid.UUID,
        status: str,
        overall_score: Optional[float] = None,
    ) -> Optional[DBPeerReviewManuscript]:
        """Update review status and composite score of a manuscript."""
        manuscript = await self.get_manuscript(manuscript_id)
        if not manuscript:
            return None

        manuscript.status = status
        if overall_score is not None:
            manuscript.overall_score = overall_score
        manuscript.updated_at = datetime.now(timezone.utc)

        await self.session.commit()
        await self.session.refresh(manuscript)
        return manuscript

    async def save_peer_review_reports(
        self,
        manuscript_id: uuid.UUID,
        reports: List[DBPeerReviewReport],
    ) -> List[DBPeerReviewReport]:
        """Persist referee reports and recalculate manuscript overall score."""
        for r in reports:
            r.manuscript_id = manuscript_id
            self.session.add(r)

        await self.session.commit()

        # Recalculate composite average score
        stmt = select(func.avg(DBPeerReviewReport.composite_score)).where(
            DBPeerReviewReport.manuscript_id == manuscript_id
        )
        avg_score_res = await self.session.execute(stmt)
        avg_score = avg_score_res.scalar() or 0.0

        manuscript = await self.get_manuscript(manuscript_id)
        if manuscript:
            manuscript.overall_score = round(float(avg_score), 2)
            # Decide stage based on referee recommendations
            recs = [r.recommendation for r in reports]
            if all(rec == "accept" for rec in recs):
                manuscript.status = "accepted"
            elif any(rec == "reject" for rec in recs) and recs.count("reject") >= 2:
                manuscript.status = "rejected"
            elif any(rec in ("minor_revision", "major_revision") for rec in recs):
                manuscript.status = "revisions_requested"
            else:
                manuscript.status = "under_review"

            await self.session.commit()
            await self.session.refresh(manuscript)

        return reports

    async def add_manuscript_revision(
        self,
        revision: DBManuscriptRevision,
    ) -> DBManuscriptRevision:
        """Record an author revision round and point-by-point response."""
        self.session.add(revision)
        manuscript = await self.get_manuscript(revision.manuscript_id)
        if manuscript:
            manuscript.status = "under_review"
            manuscript.updated_at = datetime.now(timezone.utc)

        await self.session.commit()
        await self.session.refresh(revision)
        return revision

    async def publish_manuscript(
        self,
        manuscript_id: uuid.UUID,
        doi: str,
        latex: str,
        bibtex: str,
    ) -> Optional[DBPeerReviewManuscript]:
        """Mark manuscript as published with camera-ready LaTeX, BibTeX, and DOI."""
        manuscript = await self.get_manuscript(manuscript_id)
        if not manuscript:
            return None

        manuscript.status = "published"
        manuscript.camera_ready_doi = doi
        manuscript.published_latex = latex
        manuscript.bibtex_citation = bibtex
        manuscript.updated_at = datetime.now(timezone.utc)

        await self.session.commit()
        await self.session.refresh(manuscript)
        return manuscript

    async def delete_manuscript(self, manuscript_id: uuid.UUID) -> bool:
        """Delete manuscript and associated referee reports and revisions."""
        stmt = delete(DBPeerReviewManuscript).where(DBPeerReviewManuscript.id == manuscript_id)
        res = await self.session.execute(stmt)
        await self.session.commit()
        return (res.rowcount or 0) > 0

    async def get_peer_review_metrics(
        self,
        workspace_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, Any]:
        """Query platform-wide peer review and publication statistics."""
        manuscript_stmt = select(func.count(DBPeerReviewManuscript.id))
        report_stmt = select(func.count(DBPeerReviewReport.id))
        avg_score_stmt = select(func.avg(DBPeerReviewManuscript.overall_score))

        if workspace_id:
            manuscript_stmt = manuscript_stmt.where(DBPeerReviewManuscript.workspace_id == workspace_id)

        total_manuscripts = (await self.session.execute(manuscript_stmt)).scalar() or 0
        total_reports = (await self.session.execute(report_stmt)).scalar() or 0
        avg_score = (await self.session.execute(avg_score_stmt)).scalar() or 0.0

        # Status distribution
        status_stmt = select(DBPeerReviewManuscript.status, func.count(DBPeerReviewManuscript.id)).group_by(DBPeerReviewManuscript.status)
        if workspace_id:
            status_stmt = status_stmt.where(DBPeerReviewManuscript.workspace_id == workspace_id)
        status_rows = (await self.session.execute(status_stmt)).all()
        status_dist = {row[0]: row[1] for row in status_rows}

        return {
            "total_manuscripts": total_manuscripts,
            "total_referee_reports": total_reports,
            "average_manuscript_score": round(float(avg_score), 2),
            "status_distribution": status_dist,
            "acceptance_rate": round((status_dist.get("accepted", 0) + status_dist.get("published", 0)) / max(1, total_manuscripts), 4),
        }
