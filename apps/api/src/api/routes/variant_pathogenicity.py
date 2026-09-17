"""REST API endpoints for Genomic Variant Pathogenicity & ACMG Classification."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.models import User
from database.repositories.variant_pathogenicity_repo import VariantPathogenicityRepository
from research.genomics.variant_pathogenicity_engine import VariantPathogenicityEngine

router = APIRouter(prefix="/api/v1/genomic-variants", tags=["Genomic Variant Pathogenicity & ACMG"])
engine = VariantPathogenicityEngine()


class VariantClassificationRequest(BaseModel):
    gene_symbol: str
    hgvs_c: str
    hgvs_p: str
    chromosome: str = "chr17"
    genomic_position: int = 43044295
    ref_allele: str = "C"
    alt_allele: str = "CC"
    transcript_id: str = "NM_007294.4"
    consequence: str = "frameshift_variant"
    allele_frequency_gnomad: float = Field(0.00001, ge=0.0, le=1.0)
    is_gene_lof_mechanism: bool = True
    in_critical_domain: bool = True
    is_canonical_splice: bool = False
    functional_assay_abnormal: Optional[bool] = None
    alphamissense_score: float = Field(0.85, ge=0.0, le=1.0)
    cadd_phred: float = Field(28.0, ge=0.0, le=99.0)
    revel_score: float = Field(0.75, ge=0.0, le=1.0)
    spliceai_delta_score: float = Field(0.05, ge=0.0, le=1.0)
    clinvar_id: Optional[str] = None


@router.post("/classify", status_code=status.HTTP_201_CREATED)
async def classify_variant(
    req: VariantClassificationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Classifies a genetic variant, evaluates ACMG/AMP rules, runs in-silico predictors, and persists records."""
    repo = VariantPathogenicityRepository(db)

    eval_res = engine.evaluate_variant(req.model_dump())

    report = await repo.create_report(
        gene_symbol=eval_res["gene_symbol"],
        hgvs_c=eval_res["hgvs_c"],
        hgvs_p=eval_res["hgvs_p"],
        chromosome=eval_res["chromosome"],
        genomic_position=eval_res["genomic_position"],
        ref_allele=eval_res["ref_allele"],
        alt_allele=eval_res["alt_allele"],
        transcript_id=eval_res["transcript_id"],
        acmg_class=eval_res["acmg_class"],
        pathogenicity_score=eval_res["pathogenicity_score"],
        total_criteria_met=eval_res["total_criteria_met"],
        clinvar_id=eval_res["clinvar_id"],
        variant_summary_json=eval_res["variant_summary_json"],
    )

    created_criteria = await repo.add_criteria(report.id, eval_res["criteria"])
    created_scores = await repo.add_predictor_scores(report.id, eval_res["predictor_scores"])

    return {
        "id": report.id,
        "gene_symbol": report.gene_symbol,
        "hgvs_c": report.hgvs_c,
        "hgvs_p": report.hgvs_p,
        "chromosome": report.chromosome,
        "genomic_position": report.genomic_position,
        "acmg_class": report.acmg_class,
        "pathogenicity_score": report.pathogenicity_score,
        "total_criteria_met": report.total_criteria_met,
        "clinvar_id": report.clinvar_id,
        "criteria": [
            {
                "criterion_code": c.criterion_code,
                "criterion_type": c.criterion_type,
                "status": c.status,
                "weight": c.weight,
                "rationale": c.rationale,
                "evidence_source": c.evidence_source,
            }
            for c in created_criteria
        ],
        "predictor_scores": [
            {
                "tool_name": s.tool_name,
                "score_value": s.score_value,
                "score_percentile": s.score_percentile,
                "prediction_label": s.prediction_label,
            }
            for s in created_scores
        ]
    }


@router.get("/reports")
async def list_reports(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists variant classification reports."""
    repo = VariantPathogenicityRepository(db)
    reports = await repo.list_reports(limit=limit, offset=offset)
    return [
        {
            "id": r.id,
            "gene_symbol": r.gene_symbol,
            "hgvs_c": r.hgvs_c,
            "hgvs_p": r.hgvs_p,
            "acmg_class": r.acmg_class,
            "pathogenicity_score": r.pathogenicity_score,
            "clinvar_id": r.clinvar_id,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reports
    ]


@router.get("/reports/{report_id}")
async def get_report_details(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Gets complete variant report with all ACMG criteria and in-silico predictor scores."""
    repo = VariantPathogenicityRepository(db)
    report = await repo.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Variant classification report not found")

    criteria = await repo.get_criteria_by_report(report_id)
    scores = await repo.get_predictor_scores_by_report(report_id)

    return {
        "id": report.id,
        "gene_symbol": report.gene_symbol,
        "hgvs_c": report.hgvs_c,
        "hgvs_p": report.hgvs_p,
        "chromosome": report.chromosome,
        "genomic_position": report.genomic_position,
        "ref_allele": report.ref_allele,
        "alt_allele": report.alt_allele,
        "transcript_id": report.transcript_id,
        "acmg_class": report.acmg_class,
        "pathogenicity_score": report.pathogenicity_score,
        "total_criteria_met": report.total_criteria_met,
        "clinvar_id": report.clinvar_id,
        "variant_summary": report.variant_summary_json,
        "criteria": [
            {
                "id": c.id,
                "criterion_code": c.criterion_code,
                "criterion_type": c.criterion_type,
                "status": c.status,
                "weight": c.weight,
                "rationale": c.rationale,
                "evidence_source": c.evidence_source,
            }
            for c in criteria
        ],
        "predictor_scores": [
            {
                "id": s.id,
                "tool_name": s.tool_name,
                "score_value": s.score_value,
                "score_percentile": s.score_percentile,
                "prediction_label": s.prediction_label,
            }
            for s in scores
        ]
    }
