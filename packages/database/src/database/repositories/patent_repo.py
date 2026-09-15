"""Repository for Patent Landscape Corpora, Documents, Claims, and FTO Reports."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import delete, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.patent import (
    DBFreedomToOperateReport,
    DBPatentClaim,
    DBPatentCorpus,
    DBPatentDocument,
    DBPriorArtEvaluation,
)
from shared.logging import get_logger

logger = get_logger(__name__)


class PatentRepository:
    """Async database repository for patent landscape studies, claim charts, and FTO clearance."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_corpus(self, corpus: DBPatentCorpus) -> DBPatentCorpus:
        """Create a new patent landscape study corpus."""
        self.session.add(corpus)
        await self.session.commit()
        await self.session.refresh(corpus)
        logger.info("Created patent corpus", corpus_id=str(corpus.id), title=corpus.title)
        return corpus

    async def get_corpus(self, corpus_id: uuid.UUID) -> Optional[DBPatentCorpus]:
        """Fetch corpus with child patents, claim charts, and FTO reports loaded."""
        stmt = (
            select(DBPatentCorpus)
            .options(
                selectinload(DBPatentCorpus.patents).selectinload(DBPatentDocument.claims),
                selectinload(DBPatentCorpus.evaluations),
                selectinload(DBPatentCorpus.fto_reports),
            )
            .execution_options(populate_existing=True)
            .where(DBPatentCorpus.id == corpus_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_corpora(
        self,
        user_id: Optional[uuid.UUID] = None,
        workspace_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        jurisdiction: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBPatentCorpus]:
        """List patent landscape corpora."""
        stmt = select(DBPatentCorpus).order_by(desc(DBPatentCorpus.created_at))

        if user_id:
            stmt = stmt.where(DBPatentCorpus.user_id == user_id)
        if workspace_id:
            stmt = stmt.where(DBPatentCorpus.workspace_id == workspace_id)
        if project_id:
            stmt = stmt.where(DBPatentCorpus.project_id == project_id)
        if jurisdiction:
            stmt = stmt.where(DBPatentCorpus.jurisdiction == jurisdiction)

        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_patent(self, patent: DBPatentDocument) -> DBPatentDocument:
        """Add an individual patent document asset to a corpus."""
        self.session.add(patent)
        await self.session.commit()
        await self.session.refresh(patent)
        return patent

    async def batch_add_patents(
        self,
        corpus_id: uuid.UUID,
        patents: List[DBPatentDocument],
    ) -> int:
        """Batch insert patent documents and update corpus indexed count."""
        for p in patents:
            p.corpus_id = corpus_id
            self.session.add(p)

        stmt = select(DBPatentCorpus).where(DBPatentCorpus.id == corpus_id)
        res = await self.session.execute(stmt)
        corpus = res.scalars().first()
        if corpus:
            corpus.total_patents_indexed = (corpus.total_patents_indexed or 0) + len(patents)
            corpus.updated_at = datetime.now(timezone.utc)

        await self.session.commit()
        return len(patents)

    async def add_claim(self, claim: DBPatentClaim) -> DBPatentClaim:
        """Add a patent claim limitation."""
        self.session.add(claim)
        await self.session.commit()
        await self.session.refresh(claim)
        return claim

    async def record_prior_art_evaluation(
        self,
        eval_record: DBPriorArtEvaluation,
    ) -> DBPriorArtEvaluation:
        """Save a 35 U.S.C. 102/103 novelty/non-obviousness prior art evaluation."""
        self.session.add(eval_record)
        await self.session.commit()
        await self.session.refresh(eval_record)
        return eval_record

    async def save_fto_report(
        self,
        report: DBFreedomToOperateReport,
    ) -> DBFreedomToOperateReport:
        """Save Freedom to Operate clearance report and update corpus verdict."""
        self.session.add(report)

        stmt = select(DBPatentCorpus).where(DBPatentCorpus.id == report.corpus_id)
        res = await self.session.execute(stmt)
        corpus = res.scalars().first()
        if corpus:
            if report.high_risk_claims_count > 0:
                corpus.freedom_to_operate_verdict = "high_risk"
            elif report.medium_risk_claims_count > 0:
                corpus.freedom_to_operate_verdict = "caution"
            else:
                corpus.freedom_to_operate_verdict = "clear"
            corpus.updated_at = datetime.now(timezone.utc)

        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def delete_corpus(self, corpus_id: uuid.UUID) -> bool:
        """Delete patent corpus and cascade child patents, claims, and evaluations."""
        stmt = delete(DBPatentCorpus).where(DBPatentCorpus.id == corpus_id)
        res = await self.session.execute(stmt)
        await self.session.commit()
        return (res.rowcount or 0) > 0

    async def get_patent_metrics(
        self,
        workspace_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, Any]:
        """Query platform-wide patent landscape KPIs."""
        corpus_stmt = select(func.count(DBPatentCorpus.id))
        patent_stmt = select(func.count(DBPatentDocument.id))
        eval_stmt = select(func.count(DBPriorArtEvaluation.id))
        fto_stmt = select(func.count(DBFreedomToOperateReport.id))

        if workspace_id:
            corpus_stmt = corpus_stmt.where(DBPatentCorpus.workspace_id == workspace_id)

        total_corpora = (await self.session.execute(corpus_stmt)).scalar() or 0
        total_patents = (await self.session.execute(patent_stmt)).scalar() or 0
        total_evals = (await self.session.execute(eval_stmt)).scalar() or 0
        total_ftos = (await self.session.execute(fto_stmt)).scalar() or 0

        # Jurisdiction breakdown
        jur_stmt = select(DBPatentCorpus.jurisdiction, func.count(DBPatentCorpus.id)).group_by(DBPatentCorpus.jurisdiction)
        jur_rows = (await self.session.execute(jur_stmt)).all()
        jur_dist = {row[0]: row[1] for row in jur_rows}

        # FTO verdict breakdown
        fto_verdict_stmt = select(DBPatentCorpus.freedom_to_operate_verdict, func.count(DBPatentCorpus.id)).group_by(DBPatentCorpus.freedom_to_operate_verdict)
        verdict_rows = (await self.session.execute(fto_verdict_stmt)).all()
        verdict_dist = {row[0]: row[1] for row in verdict_rows}

        return {
            "total_patent_corpora": total_corpora,
            "total_patents_indexed": total_patents,
            "total_prior_art_evaluations": total_evals,
            "total_fto_reports": total_ftos,
            "jurisdiction_distribution": jur_dist,
            "freedom_to_operate_distribution": verdict_dist,
        }
