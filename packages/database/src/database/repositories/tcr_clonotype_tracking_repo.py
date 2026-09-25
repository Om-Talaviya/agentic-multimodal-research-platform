"""Repository for TCR/BCR Clonotype Tracking & Lineage Dynamics."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.connection import AsyncSession
from database.models.tcr_clonotype_tracking import (
    DBTCRClonotypeStudy,
    DBClonotypeLineageNode,
    DBImmuneRepertoireDiversityMetric,
)


class TCRClonotypeRepository:
    """Repository handling CRUD operations for TCR/BCR Clonotype Tracking."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        study_name: str,
        sample_source: str = "PBMC",
        repertoire_type: str = "TCR_alpha_beta",
        cell_count: int = 5000,
        shannon_entropy: float = 4.52,
        gini_simpson_index: float = 0.88,
        clonality_score: float = 0.35,
        summary_metrics: Optional[Dict[str, Any]] = None,
        clonotypes: Optional[List[Dict[str, Any]]] = None,
        diversity_metrics: Optional[List[Dict[str, Any]]] = None,
    ) -> DBTCRClonotypeStudy:
        study_id = uuid.uuid4()
        study = DBTCRClonotypeStudy(
            id=study_id,
            study_name=study_name,
            sample_source=sample_source,
            repertoire_type=repertoire_type,
            cell_count=cell_count,
            shannon_entropy=shannon_entropy,
            gini_simpson_index=gini_simpson_index,
            clonality_score=clonality_score,
            summary_metrics=summary_metrics or {},
        )
        self.session.add(study)
        await self.session.flush()

        if clonotypes:
            for c in clonotypes:
                node = DBClonotypeLineageNode(
                    id=uuid.uuid4(),
                    study_id=study_id,
                    cdr3_amino_acid=c["cdr3_amino_acid"],
                    v_gene=c["v_gene"],
                    j_gene=c["j_gene"],
                    d_gene=c.get("d_gene"),
                    clone_frequency=c["clone_frequency"],
                    expansion_status=c.get("expansion_status", "hyperexpanded"),
                    antigen_specificity=c.get("antigen_specificity"),
                )
                self.session.add(node)

        if diversity_metrics:
            for d in diversity_metrics:
                metric = DBImmuneRepertoireDiversityMetric(
                    id=uuid.uuid4(),
                    study_id=study_id,
                    metric_name=d["metric_name"],
                    metric_value=d["metric_value"],
                    metric_category=d.get("metric_category", "entropy"),
                )
                self.session.add(metric)

        await self.session.commit()
        return await self.get_study(study_id)  # type: ignore

    async def get_study(self, study_id: uuid.UUID) -> Optional[DBTCRClonotypeStudy]:
        stmt = (
            select(DBTCRClonotypeStudy)
            .where(DBTCRClonotypeStudy.id == study_id)
            .options(
                selectinload(DBTCRClonotypeStudy.clonotypes),
                selectinload(DBTCRClonotypeStudy.diversity_metrics),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DBTCRClonotypeStudy]:
        stmt = (
            select(DBTCRClonotypeStudy)
            .order_by(DBTCRClonotypeStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
            .options(
                selectinload(DBTCRClonotypeStudy.clonotypes),
                selectinload(DBTCRClonotypeStudy.diversity_metrics),
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
