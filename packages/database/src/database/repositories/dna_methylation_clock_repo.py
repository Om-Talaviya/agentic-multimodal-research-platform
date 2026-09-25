"""Repository for DNA Methylation Biological Age Clocks."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.connection import AsyncSession
from database.models.dna_methylation_clock import (
    DBDNAMethylationClockStudy,
    DBCpGIslandMethylationMarker,
    DBEpigeneticAgeAccelerationMetric,
)


class DNAMethylationClockRepository:
    """Repository handling CRUD operations for DNA Methylation Clocks."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        study_name: str,
        sample_identifier: str = "DONOR-EPIGEN-01",
        tissue_type: str = "whole_blood",
        chronological_age: float = 45.0,
        horvath_predicted_age: float = 44.2,
        hannum_predicted_age: float = 43.8,
        phenoage_predicted_age: float = 46.1,
        grimage_mortality_risk_score: float = 0.22,
        age_acceleration_delta: float = -0.8,
        summary_metrics: Optional[Dict[str, Any]] = None,
        cpg_markers: Optional[List[Dict[str, Any]]] = None,
        age_metrics: Optional[List[Dict[str, Any]]] = None,
    ) -> DBDNAMethylationClockStudy:
        study_id = uuid.uuid4()
        study = DBDNAMethylationClockStudy(
            id=study_id,
            study_name=study_name,
            sample_identifier=sample_identifier,
            tissue_type=tissue_type,
            chronological_age=chronological_age,
            horvath_predicted_age=horvath_predicted_age,
            hannum_predicted_age=hannum_predicted_age,
            phenoage_predicted_age=phenoage_predicted_age,
            grimage_mortality_risk_score=grimage_mortality_risk_score,
            age_acceleration_delta=age_acceleration_delta,
            summary_metrics=summary_metrics or {},
        )
        self.session.add(study)
        await self.session.flush()

        if cpg_markers:
            for m in cpg_markers:
                marker = DBCpGIslandMethylationMarker(
                    id=uuid.uuid4(),
                    study_id=study_id,
                    cpg_probe_id=m["cpg_probe_id"],
                    target_gene=m["target_gene"],
                    chromosome=m["chromosome"],
                    genomic_coordinate=m["genomic_coordinate"],
                    beta_value=m["beta_value"],
                    clock_weight=m["clock_weight"],
                )
                self.session.add(marker)

        if age_metrics:
            for am in age_metrics:
                metric = DBEpigeneticAgeAccelerationMetric(
                    id=uuid.uuid4(),
                    study_id=study_id,
                    clock_algorithm=am["clock_algorithm"],
                    predicted_epigenetic_age=am["predicted_epigenetic_age"],
                    acceleration_residual=am["acceleration_residual"],
                    mortality_hazard_ratio=am["mortality_hazard_ratio"],
                )
                self.session.add(metric)

        await self.session.commit()
        return await self.get_study(study_id)  # type: ignore

    async def get_study(self, study_id: uuid.UUID) -> Optional[DBDNAMethylationClockStudy]:
        stmt = (
            select(DBDNAMethylationClockStudy)
            .where(DBDNAMethylationClockStudy.id == study_id)
            .options(
                selectinload(DBDNAMethylationClockStudy.cpg_markers),
                selectinload(DBDNAMethylationClockStudy.age_metrics),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DBDNAMethylationClockStudy]:
        stmt = (
            select(DBDNAMethylationClockStudy)
            .order_by(DBDNAMethylationClockStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
            .options(
                selectinload(DBDNAMethylationClockStudy.cpg_markers),
                selectinload(DBDNAMethylationClockStudy.age_metrics),
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
