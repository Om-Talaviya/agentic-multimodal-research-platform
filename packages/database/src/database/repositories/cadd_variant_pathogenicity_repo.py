"""Repository for CADD & In-Silico Variant Pathogenicity Ranker."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.connection import AsyncSession
from database.models.cadd_variant_pathogenicity import (
    DBCADDVariantStudy,
    DBCADDSNPScore,
    DBPathogenicityEnsembleScore,
)


class CADDVariantRepository:
    """Repository handling CRUD operations for CADD Variant Pathogenicity."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        study_name: str,
        genome_build: str = "GRCh38",
        target_gene: str = "TP53",
        variant_count: int = 5,
        mean_phred_score: float = 26.4,
        deleterious_variant_count: int = 3,
        summary_metrics: Optional[Dict[str, Any]] = None,
        variants: Optional[List[Dict[str, Any]]] = None,
        ensemble_scores: Optional[List[Dict[str, Any]]] = None,
    ) -> DBCADDVariantStudy:
        study_id = uuid.uuid4()
        study = DBCADDVariantStudy(
            id=study_id,
            study_name=study_name,
            genome_build=genome_build,
            target_gene=target_gene,
            variant_count=variant_count,
            mean_phred_score=mean_phred_score,
            deleterious_variant_count=deleterious_variant_count,
            summary_metrics=summary_metrics or {},
        )
        self.session.add(study)
        await self.session.flush()

        if variants:
            for v in variants:
                snp = DBCADDSNPScore(
                    id=uuid.uuid4(),
                    study_id=study_id,
                    chromosome=v["chromosome"],
                    position=v["position"],
                    reference_allele=v["reference_allele"],
                    alternate_allele=v["alternate_allele"],
                    hgvs_c=v["hgvs_c"],
                    raw_score=v["raw_score"],
                    phred_score=v["phred_score"],
                    gerp_score=v["gerp_score"],
                    phylop_score=v["phylop_score"],
                    pathogenicity_verdict=v.get("pathogenicity_verdict", "likely_deleterious"),
                )
                self.session.add(snp)

        if ensemble_scores:
            for e in ensemble_scores:
                score = DBPathogenicityEnsembleScore(
                    id=uuid.uuid4(),
                    study_id=study_id,
                    algorithm_name=e["algorithm_name"],
                    concordance_rate=e["concordance_rate"],
                    high_impact_flag=e.get("high_impact_flag", "PASS"),
                )
                self.session.add(score)

        await self.session.commit()
        return await self.get_study(study_id)  # type: ignore

    async def get_study(self, study_id: uuid.UUID) -> Optional[DBCADDVariantStudy]:
        stmt = (
            select(DBCADDVariantStudy)
            .where(DBCADDVariantStudy.id == study_id)
            .options(
                selectinload(DBCADDVariantStudy.variants),
                selectinload(DBCADDVariantStudy.ensemble_scores),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DBCADDVariantStudy]:
        stmt = (
            select(DBCADDVariantStudy)
            .order_by(DBCADDVariantStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
            .options(
                selectinload(DBCADDVariantStudy.variants),
                selectinload(DBCADDVariantStudy.ensemble_scores),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def delete_study(self, study_id: uuid.UUID) -> bool:
        study = await self.get_study(study_id)
        if not study:
            return False
        await self.session.delete(study)
        await self.session.commit()
        return True
