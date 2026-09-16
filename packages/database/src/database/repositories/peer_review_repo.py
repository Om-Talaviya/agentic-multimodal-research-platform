"""
Repository for Scientific Peer-Review Referee Panel (Phase 64).
"""
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.referee_panel import (
    DBRefereePanelManuscript,
    DBRefereePanelReport,
    DBRefereeRebuttalPoint,
)


class PeerReviewRepository:
    """Handles CRUD operations for manuscripts, adversarial referee reviews, and rebuttal arguments."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_manuscript(
        self,
        manuscript_title: str,
        research_domain: str,
        abstract_text: str,
        metadata_info: Optional[Dict[str, Any]] = None,
    ) -> DBRefereePanelManuscript:
        manuscript = DBRefereePanelManuscript(
            id=str(uuid.uuid4()),
            manuscript_title=manuscript_title,
            research_domain=research_domain,
            abstract_text=abstract_text,
            metadata_info=metadata_info or {},
        )
        self.session.add(manuscript)
        await self.session.flush()
        await self.session.commit()
        return manuscript

    async def add_reviews_and_rebuttals(
        self,
        manuscript_id: str,
        reviews_data: List[Dict[str, Any]],
        overall_score: float = 8.2,
        editorial_recommendation: str = "Accept with Minor Revisions",
    ) -> DBRefereePanelManuscript:
        for r in reviews_data:
            report = DBRefereePanelReport(
                id=str(uuid.uuid4()),
                manuscript_id=manuscript_id,
                referee_persona=r["referee_persona"],
                score_out_of_10=r["score_out_of_10"],
                statistical_rigor_score=r.get("statistical_rigor_score", 8.5),
                novelty_score=r.get("novelty_score", 9.0),
                reproducibility_score=r.get("reproducibility_score", 8.0),
                critique_summary=r["critique_summary"],
                recommendation=r.get("recommendation", "Minor Revision"),
            )
            self.session.add(report)
            await self.session.flush()

            for reb in r.get("rebuttals", []):
                pt = DBRefereeRebuttalPoint(
                    id=str(uuid.uuid4()),
                    review_id=report.id,
                    referee_claim=reb["referee_claim"],
                    author_rebuttal=reb["author_rebuttal"],
                    proposed_supplementary_experiment=reb.get("proposed_supplementary_experiment"),
                    is_conceded_and_fixed=reb.get("is_conceded_and_fixed", True),
                )
                self.session.add(pt)

        await self.session.flush()

        manuscript = await self.get_manuscript(manuscript_id)
        if manuscript:
            manuscript.total_reviews = len(reviews_data)
            manuscript.overall_score_out_of_10 = overall_score
            manuscript.editorial_recommendation = editorial_recommendation
            self.session.add(manuscript)

        await self.session.commit()
        return manuscript

    async def get_manuscript(self, manuscript_id: str) -> Optional[DBRefereePanelManuscript]:
        self.session.expire_all()
        query = (
            select(DBRefereePanelManuscript)
            .options(
                selectinload(DBRefereePanelManuscript.reviews).selectinload(DBRefereePanelReport.rebuttal_points)
            )
            .where(DBRefereePanelManuscript.id == manuscript_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_manuscripts(self, limit: int = 50) -> List[DBRefereePanelManuscript]:
        query = (
            select(DBRefereePanelManuscript)
            .options(selectinload(DBRefereePanelManuscript.reviews))
            .order_by(desc(DBRefereePanelManuscript.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
