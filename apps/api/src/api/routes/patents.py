"""REST API routes for Autonomous Patent Landscape Analysis & Prior Art Search Engine."""

import json
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db_session
from database.models.patent import (
    DBFreedomToOperateReport,
    DBPatentClaim,
    DBPatentCorpus,
    DBPatentDocument,
    DBPriorArtEvaluation,
)
from database.repositories.patent_repo import PatentRepository
from research.patents.prior_art import PatentPriorArtEngine
from shared.auth import User
from shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/patents", tags=["patents"])


# ---------------- Request & Response Schemas ----------------

class CreatePatentCorpusPayload(BaseModel):
    title: str = Field(..., min_length=3, max_length=512)
    technology_domain: str = Field(default="quantum_computing")
    cpc_classification: str = Field(default="G06N 10/00")
    jurisdiction: str = Field(default="GLOBAL", pattern="^(USPTO|EPO|WIPO|JPO|CNIPA|GLOBAL)$")
    sample_patent_count: int = Field(default=3, ge=1, le=20)
    workspace_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None


class EvaluateClaimPayload(BaseModel):
    target_invention_claim: str = Field(..., min_length=10)
    prior_art_patent_id: Optional[uuid.UUID] = None


class GenerateFTOReportPayload(BaseModel):
    target_claims: List[str] = Field(..., min_length=1)


# ---------------- Route Implementations ----------------

@router.get("/metrics")
async def get_patent_platform_metrics(
    workspace_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Query platform-wide patent landscape KPIs and FTO clearance distributions."""
    repo = PatentRepository(session)
    return await repo.get_patent_metrics(workspace_id=workspace_id)


@router.post("/corpora", status_code=status.HTTP_201_CREATED)
async def create_patent_corpus(
    payload: CreatePatentCorpusPayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Create a new patent landscape study corpus and index baseline prior art patents."""
    repo = PatentRepository(session)

    corpus = DBPatentCorpus(
        user_id=current_user.id,
        workspace_id=payload.workspace_id,
        project_id=payload.project_id,
        title=payload.title,
        technology_domain=payload.technology_domain,
        cpc_classification=payload.cpc_classification,
        jurisdiction=payload.jurisdiction,
        status="active",
    )
    created_corpus = await repo.create_corpus(corpus)

    # Synthesize baseline patent specifications
    raw_patents = PatentPriorArtEngine.synthesize_baseline_corpus(
        technology_domain=payload.technology_domain,
        cpc_classification=payload.cpc_classification,
        count=payload.sample_patent_count,
    )

    db_patents = []
    for p in raw_patents:
        doc = DBPatentDocument(
            corpus_id=created_corpus.id,
            patent_number=p["patent_number"],
            title=p["title"],
            abstract=p["abstract"],
            assignee=p["assignee"],
            filing_date=p["filing_date"],
            publication_date=p["publication_date"],
            cpc_classes=p["cpc_classes"],
            status="granted",
            claims_count=len(p.get("claims", [])),
            citations_count=12,
        )
        db_patents.append(doc)

    await repo.batch_add_patents(created_corpus.id, db_patents)

    # Add claims for the first patent
    for p_doc, p_raw in zip(db_patents, raw_patents):
        for idx, cl_text in enumerate(p_raw.get("claims", [])):
            cl = DBPatentClaim(
                patent_id=p_doc.id,
                claim_number=idx + 1,
                claim_type="independent" if idx == 0 else "dependent",
                parent_claim_number=None if idx == 0 else 1,
                claim_text=cl_text,
                parsed_elements_json=PatentPriorArtEngine.decompose_claim_limitations(cl_text)["elements"],
            )
            await repo.add_claim(cl)

    return {
        "id": str(created_corpus.id),
        "title": created_corpus.title,
        "technology_domain": created_corpus.technology_domain,
        "cpc_classification": created_corpus.cpc_classification,
        "jurisdiction": created_corpus.jurisdiction,
        "total_patents_indexed": len(db_patents),
        "status": created_corpus.status,
        "created_at": created_corpus.created_at.isoformat(),
    }


@router.get("/corpora")
async def list_patent_corpora(
    workspace_id: Optional[uuid.UUID] = Query(None),
    project_id: Optional[uuid.UUID] = Query(None),
    jurisdiction: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """List patent landscape corpora."""
    repo = PatentRepository(session)
    corpora = await repo.list_corpora(
        user_id=current_user.id if not workspace_id else None,
        workspace_id=workspace_id,
        project_id=project_id,
        jurisdiction=jurisdiction,
        limit=limit,
        offset=offset,
    )
    return [
        {
            "id": str(c.id),
            "title": c.title,
            "technology_domain": c.technology_domain,
            "cpc_classification": c.cpc_classification,
            "jurisdiction": c.jurisdiction,
            "total_patents_indexed": c.total_patents_indexed,
            "freedom_to_operate_verdict": c.freedom_to_operate_verdict,
            "status": c.status,
            "created_at": c.created_at.isoformat(),
        }
        for c in corpora
    ]


@router.get("/corpora/{corpus_id}")
async def get_patent_corpus(
    corpus_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Fetch complete patent corpus with patents, claims, prior art evaluations, and FTO reports."""
    repo = PatentRepository(session)
    corpus = await repo.get_corpus(corpus_id)
    if not corpus:
        raise HTTPException(status_code=404, detail="Patent corpus not found")

    return {
        "id": str(corpus.id),
        "title": corpus.title,
        "technology_domain": corpus.technology_domain,
        "cpc_classification": corpus.cpc_classification,
        "jurisdiction": corpus.jurisdiction,
        "total_patents_indexed": corpus.total_patents_indexed,
        "freedom_to_operate_verdict": corpus.freedom_to_operate_verdict,
        "status": corpus.status,
        "created_at": corpus.created_at.isoformat(),
        "patents": [
            {
                "id": str(p.id),
                "patent_number": p.patent_number,
                "title": p.title,
                "abstract": p.abstract,
                "assignee": p.assignee,
                "filing_date": p.filing_date,
                "publication_date": p.publication_date,
                "cpc_classes": p.cpc_classes,
                "status": p.status,
                "claims_count": len(p.claims),
                "claims": [
                    {
                        "id": str(cl.id),
                        "claim_number": cl.claim_number,
                        "claim_type": cl.claim_type,
                        "claim_text": cl.claim_text,
                        "parsed_elements": cl.parsed_elements_json,
                    }
                    for cl in p.claims
                ],
            }
            for p in corpus.patents
        ],
        "evaluations": [
            {
                "id": str(ev.id),
                "target_invention_claim": ev.target_invention_claim,
                "novelty_score": ev.novelty_score,
                "obviousness_score": ev.obviousness_score,
                "overlap_ratio": ev.overlap_ratio,
                "verdict": ev.verdict,
                "detailed_rationale": ev.detailed_rationale,
                "mitigation_strategy": ev.mitigation_strategy,
                "created_at": ev.created_at.isoformat(),
            }
            for ev in corpus.evaluations
        ],
        "fto_reports": [
            {
                "id": str(f.id),
                "total_examined_patents": f.total_examined_patents,
                "high_risk_claims_count": f.high_risk_claims_count,
                "medium_risk_claims_count": f.medium_risk_claims_count,
                "fto_clearance_percentage": f.fto_clearance_percentage,
                "summary_assessment": f.summary_assessment,
                "white_space_opportunities": f.white_space_opportunities,
                "created_at": f.created_at.isoformat(),
            }
            for f in corpus.fto_reports
        ],
    }


@router.post("/corpora/{corpus_id}/evaluate-claim", status_code=status.HTTP_201_CREATED)
async def evaluate_patent_claim(
    corpus_id: uuid.UUID,
    payload: EvaluateClaimPayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Run 35 U.S.C. 102/103 novelty and obviousness prior art search on target invention claim."""
    repo = PatentRepository(session)
    corpus = await repo.get_corpus(corpus_id)
    if not corpus:
        raise HTTPException(status_code=404, detail="Patent corpus not found")

    prior_art_texts = []
    target_prior_doc_id = payload.prior_art_patent_id

    for p in corpus.patents:
        if not target_prior_doc_id or str(p.id) == str(target_prior_doc_id):
            prior_art_texts.extend([cl.claim_text for cl in p.claims])
            if not target_prior_doc_id:
                target_prior_doc_id = p.id

    eval_result = PatentPriorArtEngine.evaluate_prior_art_anticipation(
        target_claim=payload.target_invention_claim,
        prior_art_claims=prior_art_texts if prior_art_texts else ["A system comprising hardware processors."],
    )

    eval_record = DBPriorArtEvaluation(
        corpus_id=corpus_id,
        prior_art_patent_id=target_prior_doc_id,
        target_invention_claim=payload.target_invention_claim,
        novelty_score=eval_result["novelty_score"],
        obviousness_score=eval_result["obviousness_score"],
        overlap_ratio=eval_result["overlap_ratio"],
        verdict=eval_result["verdict"],
        detailed_rationale=eval_result["detailed_rationale"],
        mitigation_strategy=eval_result["mitigation_strategy"],
    )
    saved_eval = await repo.record_prior_art_evaluation(eval_record)

    return {
        "id": str(saved_eval.id),
        "corpus_id": str(corpus_id),
        "novelty_score": saved_eval.novelty_score,
        "obviousness_score": saved_eval.obviousness_score,
        "overlap_ratio": saved_eval.overlap_ratio,
        "verdict": saved_eval.verdict,
        "detailed_rationale": saved_eval.detailed_rationale,
        "mitigation_strategy": saved_eval.mitigation_strategy,
        "claim_chart": eval_result.get("claim_chart", []),
        "created_at": saved_eval.created_at.isoformat(),
    }


@router.post("/corpora/{corpus_id}/fto-report", status_code=status.HTTP_201_CREATED)
async def generate_fto_clearance_report(
    corpus_id: uuid.UUID,
    payload: GenerateFTOReportPayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Synthesize complete Freedom to Operate (FTO) clearance report and white space opportunities."""
    repo = PatentRepository(session)
    corpus = await repo.get_corpus(corpus_id)
    if not corpus:
        raise HTTPException(status_code=404, detail="Patent corpus not found")

    patent_dicts = [
        {
            "patent_number": p.patent_number,
            "title": p.title,
            "assignee": p.assignee,
            "claims": [cl.claim_text for cl in p.claims],
            "abstract": p.abstract,
        }
        for p in corpus.patents
    ]

    fto_res = PatentPriorArtEngine.generate_fto_assessment(
        target_claims=payload.target_claims,
        patents=patent_dicts,
    )

    report = DBFreedomToOperateReport(
        corpus_id=corpus_id,
        total_examined_patents=fto_res["total_examined_patents"],
        high_risk_claims_count=fto_res["high_risk_claims_count"],
        medium_risk_claims_count=fto_res["medium_risk_claims_count"],
        fto_clearance_percentage=fto_res["fto_clearance_percentage"],
        summary_assessment=fto_res["summary_assessment"],
        white_space_opportunities=fto_res["white_space_opportunities"],
        claim_chart_matrices=fto_res["claim_chart_matrices"],
    )
    saved_report = await repo.save_fto_report(report)

    return {
        "id": str(saved_report.id),
        "corpus_id": str(corpus_id),
        "fto_clearance_percentage": saved_report.fto_clearance_percentage,
        "high_risk_claims_count": saved_report.high_risk_claims_count,
        "medium_risk_claims_count": saved_report.medium_risk_claims_count,
        "summary_assessment": saved_report.summary_assessment,
        "white_space_opportunities": saved_report.white_space_opportunities,
        "created_at": saved_report.created_at.isoformat(),
    }


@router.delete("/corpora/{corpus_id}")
async def delete_patent_corpus(
    corpus_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Delete patent corpus."""
    repo = PatentRepository(session)
    deleted = await repo.delete_corpus(corpus_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Patent corpus not found")
    return {"message": "Patent corpus deleted successfully"}
