"""
Repository for Rare Disease HPO Diagnostic Matching (Phase 61).
"""
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.rare_disease_hpo import (
    DBRareDiseaseDiagnosticCase,
    DBHPOPhenotypeTerm,
    DBCandidateGeneMatch,
)


class RareDiseaseHPORepository:
    """Handles CRUD operations for rare disease diagnostic cases and phenotype-to-gene matches."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_case(
        self,
        case_number: str,
        patient_id: str,
        clinical_summary: str,
        age_of_onset: str = "Infantile",
        metadata_info: Optional[Dict[str, Any]] = None,
    ) -> DBRareDiseaseDiagnosticCase:
        case = DBRareDiseaseDiagnosticCase(
            id=str(uuid.uuid4()),
            case_number=case_number,
            patient_id=patient_id,
            clinical_summary=clinical_summary,
            age_of_onset=age_of_onset,
            metadata_info=metadata_info or {},
        )
        self.session.add(case)
        await self.session.flush()
        await self.session.commit()
        return case

    async def add_phenotypes_and_matches(
        self,
        case_id: str,
        phenotypes_data: List[Dict[str, Any]],
        candidate_genes_data: List[Dict[str, Any]],
    ) -> DBRareDiseaseDiagnosticCase:
        for p in phenotypes_data:
            term = DBHPOPhenotypeTerm(
                id=str(uuid.uuid4()),
                case_id=case_id,
                hpo_id=p["hpo_id"],
                term_name=p["term_name"],
                severity_weight=p.get("severity_weight", 1.0),
                is_negated=p.get("is_negated", False),
                information_content=p.get("information_content", 7.5),
            )
            self.session.add(term)

        top_disease = None
        for i, g in enumerate(candidate_genes_data):
            is_top = (i == 0) or g.get("is_top_match", False)
            if is_top and not top_disease:
                top_disease = f"{g['gene_symbol']} - {g['disease_name']}"
            match = DBCandidateGeneMatch(
                id=str(uuid.uuid4()),
                case_id=case_id,
                gene_symbol=g["gene_symbol"],
                disease_name=g["disease_name"],
                omim_id=g.get("omim_id", "OMIM:000000"),
                semantic_similarity_score=g["semantic_similarity_score"],
                inheritance_mode=g.get("inheritance_mode", "Autosomal Dominant"),
                pathogenicity_evidence=g.get("pathogenicity_evidence", "ClinVar Pathogenic"),
                is_top_match=is_top,
            )
            self.session.add(match)

        await self.session.flush()

        case = await self.get_case(case_id)
        if case:
            case.total_phenotypes_mapped = len(phenotypes_data)
            case.top_predicted_disease = top_disease
            self.session.add(case)

        await self.session.commit()
        return case

    async def get_case(self, case_id: str) -> Optional[DBRareDiseaseDiagnosticCase]:
        self.session.expire_all()
        query = (
            select(DBRareDiseaseDiagnosticCase)
            .options(
                selectinload(DBRareDiseaseDiagnosticCase.phenotypes),
                selectinload(DBRareDiseaseDiagnosticCase.candidate_genes),
            )
            .where(DBRareDiseaseDiagnosticCase.id == case_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_cases(self, limit: int = 50) -> List[DBRareDiseaseDiagnosticCase]:
        query = (
            select(DBRareDiseaseDiagnosticCase)
            .options(selectinload(DBRareDiseaseDiagnosticCase.phenotypes))
            .order_by(desc(DBRareDiseaseDiagnosticCase.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
