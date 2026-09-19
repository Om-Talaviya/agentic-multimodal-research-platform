"""API Routes for Literature Discrepancy & Hallucination Fact-Checking (Phase 103)."""

import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.literature_factcheck_repo import LiteratureFactCheckRepository
from research.literature.factcheck_engine import LiteratureFactCheckEngine

router = APIRouter(prefix="/literature-factcheck", tags=["Literature Discrepancy & Fact-Checking"])


class FactCheckRequest(BaseModel):
    paper_title: str = Field(..., example="Targeting oncogenic KRAS G12D with novel quinazoline derivatives")
    doi_or_pmid: str = Field(..., example="10.1016/j.ejmech.2024.116234")
    abstract_or_text: str = Field(..., example="We report the design and synthesis of potent non-covalent inhibitors...")
    workspace_id: Optional[str] = None


@router.post("/verify", status_code=status.HTTP_201_CREATED)
async def verify_literature_claims(
    request: FactCheckRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Cross-examine claims against literature knowledge graph and audit citation fidelity."""
    engine = LiteratureFactCheckEngine()
    result = engine.factcheck_paper(
        paper_title=request.paper_title,
        doi_or_pmid=request.doi_or_pmid,
        abstract_or_text=request.abstract_or_text,
    )

    repo = LiteratureFactCheckRepository(db)
    ws_id = uuid.UUID(request.workspace_id) if request.workspace_id else uuid.uuid4()

    fc = await repo.create_factcheck(
        workspace_id=ws_id,
        paper_title=result["paper_title"],
        doi_or_pmid=result["doi_or_pmid"],
        factcheck_verdict=result["factcheck_verdict"],
        overall_truthfulness_score=result["overall_truthfulness_score"],
        total_claims_extracted=result["total_claims_extracted"],
        corroborated_claims_count=result["corroborated_claims_count"],
        discrepant_claims_count=result["discrepant_claims_count"],
        analysis_metadata={"summary": result["summary"]},
    )

    for cl in result["claims"]:
        await repo.add_discrepancy_claim(
            factcheck_id=fc.id,
            claim_text=cl["claim_text"],
            claimed_finding=cl["claimed_finding"],
            literature_consensus_finding=cl["literature_consensus_finding"],
            contradiction_severity=cl["contradiction_severity"],
            supporting_evidence_count=cl["supporting_evidence_count"],
            refuting_evidence_count=cl["refuting_evidence_count"],
        )

    for cit in result["citations"]:
        await repo.add_citation_metric(
            factcheck_id=fc.id,
            cited_doi=cit["cited_doi"],
            cited_paper_title=cit["cited_paper_title"],
            citation_context_match=cit["citation_context_match"],
            integrity_confidence=cit["integrity_confidence"],
        )

    return {
        "status": "SUCCESS",
        "factcheck_id": str(fc.id),
        "paper_title": fc.paper_title,
        "factcheck_verdict": fc.factcheck_verdict,
        "overall_truthfulness_score": fc.overall_truthfulness_score,
        "claims": result["claims"],
        "citations": result["citations"],
        "summary": result["summary"],
    }


@router.get("/factchecks/{factcheck_id}")
async def get_factcheck_details(
    factcheck_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Retrieve full literature fact-check scorecard and claim refutations."""
    repo = LiteratureFactCheckRepository(db)
    try:
        fid = uuid.UUID(factcheck_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid factcheck UUID format")

    fc = await repo.get_factcheck(fid)
    if not fc:
        raise HTTPException(status_code=404, detail="Factcheck not found")

    return {
        "id": str(fc.id),
        "paper_title": fc.paper_title,
        "doi_or_pmid": fc.doi_or_pmid,
        "factcheck_verdict": fc.factcheck_verdict,
        "overall_truthfulness_score": fc.overall_truthfulness_score,
        "claims": [
            {
                "claim_text": c.claim_text,
                "claimed": c.claimed_finding,
                "consensus": c.literature_consensus_finding,
                "severity": c.contradiction_severity,
            }
            for c in fc.claims
        ],
        "citations": [
            {
                "doi": cit.cited_doi,
                "title": cit.cited_paper_title,
                "status": cit.citation_context_match,
            }
            for cit in fc.citations
        ],
    }
