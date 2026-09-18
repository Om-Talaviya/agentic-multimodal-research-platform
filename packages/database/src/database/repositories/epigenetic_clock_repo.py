"""Repository for Epigenetic Clocks and DNA Methylation Analysis."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from database.models.epigenetic_clock import (
    DBEpigeneticSample,
    DBMethylationClockResult,
    DBCpGMarkerScore,
)


class EpigeneticClockRepository:
    """Repository handling CRUD operations for Epigenetic clock datasets and results."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_sample(
        self,
        workspace_id: UUID,
        sample_name: str,
        chronological_age: float,
        tissue_type: str = "Whole Blood",
        gender: str = "unknown",
        platform: str = "Illumina EPIC 850k",
        total_cpgs_profiled: int = 0,
        sample_metadata: Optional[Dict[str, Any]] = None,
    ) -> DBEpigeneticSample:
        sample = DBEpigeneticSample(
            workspace_id=workspace_id,
            sample_name=sample_name,
            chronological_age=chronological_age,
            tissue_type=tissue_type,
            gender=gender,
            platform=platform,
            total_cpgs_profiled=total_cpgs_profiled,
            sample_metadata=sample_metadata or {},
        )
        self.session.add(sample)
        await self.session.commit()
        await self.session.refresh(sample)
        return sample

    async def get_sample(self, sample_id: UUID) -> Optional[DBEpigeneticSample]:
        query = (
            select(DBEpigeneticSample)
            .where(DBEpigeneticSample.id == sample_id)
            .options(
                selectinload(DBEpigeneticSample.clock_results).selectinload(DBMethylationClockResult.cpg_markers)
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_samples(self, workspace_id: UUID, limit: int = 50, offset: int = 0) -> List[DBEpigeneticSample]:
        query = (
            select(DBEpigeneticSample)
            .where(DBEpigeneticSample.workspace_id == workspace_id)
            .order_by(desc(DBEpigeneticSample.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_clock_result(
        self,
        sample_id: UUID,
        predicted_epigenetic_age: float,
        age_acceleration: float,
        clock_model: str = "Horvath Multi-Tissue",
        confidence_interval_low: float = 0.0,
        confidence_interval_high: float = 0.0,
        mortality_risk_percentile: float = 50.0,
        model_r_squared: float = 0.92,
        cpgs_utilized: int = 353,
        pace_of_aging: float = 1.0,
        analysis_details: Optional[Dict[str, Any]] = None,
        cpg_markers: Optional[List[Dict[str, Any]]] = None,
    ) -> DBMethylationClockResult:
        result = DBMethylationClockResult(
            sample_id=sample_id,
            clock_model=clock_model,
            predicted_epigenetic_age=predicted_epigenetic_age,
            age_acceleration=age_acceleration,
            confidence_interval_low=confidence_interval_low,
            confidence_interval_high=confidence_interval_high,
            mortality_risk_percentile=mortality_risk_percentile,
            model_r_squared=model_r_squared,
            cpgs_utilized=cpgs_utilized,
            pace_of_aging=pace_of_aging,
            analysis_details=analysis_details or {},
        )
        self.session.add(result)
        await self.session.flush()

        if cpg_markers:
            for marker in cpg_markers:
                score = DBCpGMarkerScore(
                    clock_result_id=result.id,
                    cpg_id=marker.get("cpg_id", "cg00000000"),
                    gene_symbol=marker.get("gene_symbol"),
                    chromosome=marker.get("chromosome"),
                    genomic_coordinate=marker.get("genomic_coordinate"),
                    beta_value=marker.get("beta_value", 0.5),
                    model_weight=marker.get("model_weight", 0.0),
                    contribution_to_age=marker.get("contribution_to_age", 0.0),
                )
                self.session.add(score)

        await self.session.commit()
        await self.session.refresh(result)
        return result

    async def get_clock_result(self, result_id: UUID) -> Optional[DBMethylationClockResult]:
        query = (
            select(DBMethylationClockResult)
            .where(DBMethylationClockResult.id == result_id)
            .options(selectinload(DBMethylationClockResult.cpg_markers))
        )
        res = await self.session.execute(query)
        return res.scalars().first()
