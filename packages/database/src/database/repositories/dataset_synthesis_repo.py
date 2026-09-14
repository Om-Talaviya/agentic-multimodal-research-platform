"""Repository for Synthetic Instruction Tuning Datasets, Samples, and Alignment Exports."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import delete, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.dataset_synthesis import (
    DBAlignmentExport,
    DBInstructionSample,
    DBSyntheticDataset,
)
from shared.logging import get_logger

logger = get_logger(__name__)


class DatasetSynthesisRepository:
    """Async database repository for synthetic dataset generation, active learning curation, and export."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_dataset(self, dataset: DBSyntheticDataset) -> DBSyntheticDataset:
        """Create a synthetic dataset record."""
        self.session.add(dataset)
        await self.session.commit()
        await self.session.refresh(dataset)
        logger.info("Created synthetic dataset", dataset_id=str(dataset.id), name=dataset.name)
        return dataset

    async def get_dataset(self, dataset_id: uuid.UUID) -> Optional[DBSyntheticDataset]:
        """Fetch dataset with all child samples and exports loaded."""
        stmt = (
            select(DBSyntheticDataset)
            .options(
                selectinload(DBSyntheticDataset.samples),
                selectinload(DBSyntheticDataset.exports),
            )
            .execution_options(populate_existing=True)
            .where(DBSyntheticDataset.id == dataset_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_datasets(
        self,
        user_id: Optional[uuid.UUID] = None,
        workspace_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        dataset_format: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBSyntheticDataset]:
        """List synthetic datasets with optional workspace and format filtering."""
        stmt = select(DBSyntheticDataset).order_by(desc(DBSyntheticDataset.created_at))

        if user_id:
            stmt = stmt.where(DBSyntheticDataset.user_id == user_id)
        if workspace_id:
            stmt = stmt.where(DBSyntheticDataset.workspace_id == workspace_id)
        if project_id:
            stmt = stmt.where(DBSyntheticDataset.project_id == project_id)
        if dataset_format:
            stmt = stmt.where(DBSyntheticDataset.dataset_format == dataset_format)

        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_dataset_status(
        self,
        dataset_id: uuid.UUID,
        status: str,
        total_samples: Optional[int] = None,
    ) -> Optional[DBSyntheticDataset]:
        """Update dataset processing status and sample counts."""
        dataset = await self.get_dataset(dataset_id)
        if not dataset:
            return None

        dataset.status = status
        if total_samples is not None:
            dataset.total_samples = total_samples
        dataset.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(dataset)
        return dataset

    async def add_sample(self, sample: DBInstructionSample) -> DBInstructionSample:
        """Add a single instruction sample to a dataset."""
        self.session.add(sample)
        await self.session.commit()
        await self.session.refresh(sample)
        return sample

    async def batch_add_samples(
        self,
        dataset_id: uuid.UUID,
        samples: List[DBInstructionSample],
    ) -> int:
        """Batch insert instruction samples and update dataset total count."""
        for s in samples:
            s.dataset_id = dataset_id
            self.session.add(s)

        # Increment total_samples
        stmt = select(DBSyntheticDataset).where(DBSyntheticDataset.id == dataset_id)
        res = await self.session.execute(stmt)
        dataset = res.scalars().first()
        if dataset:
            dataset.total_samples = (dataset.total_samples or 0) + len(samples)
            dataset.updated_at = datetime.now(timezone.utc)

        await self.session.commit()
        return len(samples)

    async def update_sample_curation(
        self,
        sample_id: uuid.UUID,
        verdict: str,
        quality_score: Optional[float] = None,
        chosen_response: Optional[str] = None,
    ) -> Optional[DBInstructionSample]:
        """Update human active-learning curation verdict and edited response."""
        stmt = select(DBInstructionSample).where(DBInstructionSample.id == sample_id)
        result = await self.session.execute(stmt)
        sample = result.scalars().first()
        if not sample:
            return None

        sample.curation_verdict = verdict
        if quality_score is not None:
            sample.quality_score = quality_score
        if chosen_response is not None:
            sample.chosen_response = chosen_response

        await self.session.commit()
        await self.session.refresh(sample)
        return sample

    async def record_export(self, export: DBAlignmentExport) -> DBAlignmentExport:
        """Record an exported dataset artifact."""
        self.session.add(export)
        await self.session.commit()
        await self.session.refresh(export)
        return export

    async def delete_dataset(self, dataset_id: uuid.UUID) -> bool:
        """Delete dataset and cascade child samples/exports."""
        stmt = delete(DBSyntheticDataset).where(DBSyntheticDataset.id == dataset_id)
        res = await self.session.execute(stmt)
        await self.session.commit()
        return (res.rowcount or 0) > 0

    async def get_synthesis_metrics(
        self,
        workspace_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, Any]:
        """Query platform-wide synthetic data generation metrics."""
        ds_stmt = select(func.count(DBSyntheticDataset.id))
        sample_stmt = select(func.count(DBInstructionSample.id))
        export_stmt = select(func.count(DBAlignmentExport.id))
        avg_quality_stmt = select(func.avg(DBInstructionSample.quality_score))

        if workspace_id:
            ds_stmt = ds_stmt.where(DBSyntheticDataset.workspace_id == workspace_id)

        total_datasets = (await self.session.execute(ds_stmt)).scalar() or 0
        total_samples = (await self.session.execute(sample_stmt)).scalar() or 0
        total_exports = (await self.session.execute(export_stmt)).scalar() or 0
        avg_quality = (await self.session.execute(avg_quality_stmt)).scalar() or 0.0

        # Format breakdown
        fmt_stmt = select(DBSyntheticDataset.dataset_format, func.count(DBSyntheticDataset.id)).group_by(DBSyntheticDataset.dataset_format)
        fmt_rows = (await self.session.execute(fmt_stmt)).all()
        fmt_dist = {row[0]: row[1] for row in fmt_rows}

        # Strategy breakdown
        strat_stmt = select(DBInstructionSample.evolution_strategy, func.count(DBInstructionSample.id)).group_by(DBInstructionSample.evolution_strategy)
        strat_rows = (await self.session.execute(strat_stmt)).all()
        strat_dist = {row[0]: row[1] for row in strat_rows}

        return {
            "total_synthetic_datasets": total_datasets,
            "total_instruction_samples": total_samples,
            "total_alignment_exports": total_exports,
            "average_quality_score": round(float(avg_quality), 3),
            "format_distribution": fmt_dist,
            "evolution_strategy_distribution": strat_dist,
        }
