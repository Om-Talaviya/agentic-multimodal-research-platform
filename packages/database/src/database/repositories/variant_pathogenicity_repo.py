"""Repository for Genomic Variant Pathogenicity & ACMG Classification."""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database.models.variant_pathogenicity import (
    DBVariantClassificationReport,
    DBACMGCriterionEvidence,
    DBInSilicoPredictorScore,
)


class VariantPathogenicityRepository:
    """Handles async database operations for variant pathogenicity classification."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_report(
        self,
        gene_symbol: str,
        hgvs_c: str,
        hgvs_p: str,
        chromosome: str,
        genomic_position: int,
        ref_allele: str,
        alt_allele: str,
        transcript_id: str,
        acmg_class: str,
        pathogenicity_score: float,
        total_criteria_met: int,
        clinvar_id: Optional[str] = None,
        variant_summary_json: Optional[Dict[str, Any]] = None,
    ) -> DBVariantClassificationReport:
        report = DBVariantClassificationReport(
            gene_symbol=gene_symbol,
            hgvs_c=hgvs_c,
            hgvs_p=hgvs_p,
            chromosome=chromosome,
            genomic_position=genomic_position,
            ref_allele=ref_allele,
            alt_allele=alt_allele,
            transcript_id=transcript_id,
            acmg_class=acmg_class,
            pathogenicity_score=pathogenicity_score,
            total_criteria_met=total_criteria_met,
            clinvar_id=clinvar_id,
            variant_summary_json=variant_summary_json or {},
        )
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def get_report(self, report_id: str) -> Optional[DBVariantClassificationReport]:
        stmt = select(DBVariantClassificationReport).where(DBVariantClassificationReport.id == report_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_reports(self, limit: int = 50, offset: int = 0) -> List[DBVariantClassificationReport]:
        stmt = select(DBVariantClassificationReport).order_by(desc(DBVariantClassificationReport.created_at)).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_criteria(
        self,
        report_id: str,
        criteria_data: List[Dict[str, Any]],
    ) -> List[DBACMGCriterionEvidence]:
        created = []
        for c in criteria_data:
            crit = DBACMGCriterionEvidence(
                report_id=report_id,
                criterion_code=c["criterion_code"],
                criterion_type=c["criterion_type"],
                status=c.get("status", "NOT_MET"),
                weight=c.get("weight", 1.0),
                rationale=c.get("rationale", ""),
                evidence_source=c.get("evidence_source", "ACMG Evaluator"),
            )
            self.session.add(crit)
            created.append(crit)
        await self.session.commit()
        for item in created:
            await self.session.refresh(item)
        return created

    async def get_criteria_by_report(self, report_id: str) -> List[DBACMGCriterionEvidence]:
        stmt = select(DBACMGCriterionEvidence).where(DBACMGCriterionEvidence.report_id == report_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_predictor_scores(
        self,
        report_id: str,
        scores_data: List[Dict[str, Any]],
    ) -> List[DBInSilicoPredictorScore]:
        created = []
        for s in scores_data:
            score = DBInSilicoPredictorScore(
                report_id=report_id,
                tool_name=s["tool_name"],
                score_value=s["score_value"],
                score_percentile=s.get("score_percentile", 50.0),
                prediction_label=s["prediction_label"],
            )
            self.session.add(score)
            created.append(score)
        await self.session.commit()
        for item in created:
            await self.session.refresh(item)
        return created

    async def get_predictor_scores_by_report(self, report_id: str) -> List[DBInSilicoPredictorScore]:
        stmt = select(DBInSilicoPredictorScore).where(DBInSilicoPredictorScore.report_id == report_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
