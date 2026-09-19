"""Repository for Literature Discrepancy & Fact-Checking data access (Phase 103)."""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.models.literature_factcheck import (
    DBLiteratureFactCheck,
    DBDiscrepancyClaim,
    DBCitationIntegrityMetric,
)


class LiteratureFactCheckRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_factcheck(
        self,
        workspace_id: uuid.UUID,
        paper_title: str,
        doi_or_pmid: str,
        factcheck_verdict: str = "VERIFIED_CONSISTENT",
        overall_truthfulness_score: float = 94.5,
        total_claims_extracted: int = 18,
        corroborated_claims_count: int = 16,
        discrepant_claims_count: int = 2,
        analysis_metadata: Optional[Dict[str, Any]] = None,
    ) -> DBLiteratureFactCheck:
        fc = DBLiteratureFactCheck(
            workspace_id=workspace_id,
            paper_title=paper_title,
            doi_or_pmid=doi_or_pmid,
            factcheck_verdict=factcheck_verdict,
            overall_truthfulness_score=overall_truthfulness_score,
            total_claims_extracted=total_claims_extracted,
            corroborated_claims_count=corroborated_claims_count,
            discrepant_claims_count=discrepant_claims_count,
            analysis_metadata=analysis_metadata or {},
        )
        self.session.add(fc)
        await self.session.commit()
        await self.session.refresh(fc)
        return fc

    async def add_discrepancy_claim(
        self,
        factcheck_id: uuid.UUID,
        claim_text: str,
        claimed_finding: str,
        literature_consensus_finding: str,
        contradiction_severity: str = "MEDIUM",
        supporting_evidence_count: int = 8,
        refuting_evidence_count: int = 12,
    ) -> DBDiscrepancyClaim:
        claim = DBDiscrepancyClaim(
            factcheck_id=factcheck_id,
            claim_text=claim_text,
            claimed_finding=claimed_finding,
            literature_consensus_finding=literature_consensus_finding,
            contradiction_severity=contradiction_severity,
            supporting_evidence_count=supporting_evidence_count,
            refuting_evidence_count=refuting_evidence_count,
        )
        self.session.add(claim)
        await self.session.commit()
        await self.session.refresh(claim)
        return claim

    async def add_citation_metric(
        self,
        factcheck_id: uuid.UUID,
        cited_doi: str,
        cited_paper_title: str,
        citation_context_match: str = "FAITHFUL_CITATION",
        integrity_confidence: float = 0.96,
    ) -> DBCitationIntegrityMetric:
        cit = DBCitationIntegrityMetric(
            factcheck_id=factcheck_id,
            cited_doi=cited_doi,
            cited_paper_title=cited_paper_title,
            citation_context_match=citation_context_match,
            integrity_confidence=integrity_confidence,
        )
        self.session.add(cit)
        await self.session.commit()
        await self.session.refresh(cit)
        return cit

    async def get_factcheck(self, factcheck_id: uuid.UUID) -> Optional[DBLiteratureFactCheck]:
        stmt = (
            select(DBLiteratureFactCheck)
            .options(
                selectinload(DBLiteratureFactCheck.claims),
                selectinload(DBLiteratureFactCheck.citations),
            )
            .where(DBLiteratureFactCheck.id == factcheck_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
