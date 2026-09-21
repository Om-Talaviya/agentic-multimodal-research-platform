"""Preprint Latex Repo (Phase 124)."""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.preprint_latex import DBPreprintManuscript, DBCitationGraphNode

class PreprintLatexRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_manuscript(self, workspace_id: uuid.UUID, manuscript_title: str,
                                journal_target_format: str, total_words: int,
                                compilation_status: str, latex_source_code: str) -> DBPreprintManuscript:
        m = DBPreprintManuscript(
            workspace_id=workspace_id,
            manuscript_title=manuscript_title,
            journal_target_format=journal_target_format,
            total_words=total_words,
            compilation_status=compilation_status,
            latex_source_code=latex_source_code,
        )
        self.db.add(m)
        await self.db.commit()
        await self.db.refresh(m)
        return m

    async def add_citation(self, manuscript_id: uuid.UUID, citation_key: str,
                           doi_or_pmid: str, bibtex_entry: str,
                           verified_valid: float = 1.0) -> DBCitationGraphNode:
        c = DBCitationGraphNode(
            manuscript_id=manuscript_id,
            citation_key=citation_key,
            doi_or_pmid=doi_or_pmid,
            bibtex_entry=bibtex_entry,
            verified_valid=verified_valid,
        )
        self.db.add(c)
        await self.db.commit()
        await self.db.refresh(c)
        return c

    async def get_manuscript(self, manuscript_id: uuid.UUID) -> Optional[DBPreprintManuscript]:
        res = await self.db.execute(select(DBPreprintManuscript).where(DBPreprintManuscript.id == manuscript_id))
        return res.scalar_one_or_none()
