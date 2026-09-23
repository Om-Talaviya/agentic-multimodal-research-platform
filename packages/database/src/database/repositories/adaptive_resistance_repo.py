"""Repository for Phase 130: Precision Oncology Adaptive Chemotherapy Resistance & Clonal Fitness Dynamics."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from database.models.adaptive_resistance import (
    DBAdaptiveResistanceStudy,
    DBClonalFitnessLineage,
    DBDrugResistanceTrajectory,
)


class AdaptiveResistanceRepository:
    """Repository handling CRUD operations for adaptive resistance studies."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        cancer_type: str,
        patient_id: Optional[str] = None,
        description: Optional[str] = None,
        chemo_regimen: Optional[List[Dict[str, Any]]] = None,
        total_cycles: int = 10,
        summary_metrics: Optional[Dict[str, Any]] = None,
    ) -> DBAdaptiveResistanceStudy:
        """Create a new adaptive resistance study."""
        study = DBAdaptiveResistanceStudy(
            id=uuid.uuid4(),
            name=name,
            cancer_type=cancer_type,
            patient_id=patient_id,
            description=description,
            chemo_regimen=chemo_regimen or [],
            total_cycles=total_cycles,
            summary_metrics=summary_metrics or {},
        )
        self.session.add(study)
        await self.session.commit()
        await self.session.refresh(study)
        return study

    async def get_study(self, study_id: uuid.UUID) -> Optional[DBAdaptiveResistanceStudy]:
        """Get study by ID."""
        stmt = (
            select(DBAdaptiveResistanceStudy)
            .options(
                selectinload(DBAdaptiveResistanceStudy.clonal_lineages),
                selectinload(DBAdaptiveResistanceStudy.resistance_trajectories),
            )
            .where(DBAdaptiveResistanceStudy.id == study_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DBAdaptiveResistanceStudy]:
        """List all adaptive resistance studies."""
        stmt = (
            select(DBAdaptiveResistanceStudy)
            .order_by(desc(DBAdaptiveResistanceStudy.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_clonal_lineage(
        self,
        study_id: uuid.UUID,
        clone_name: str,
        driver_mutations: List[str],
        initial_frequency: float = 0.1,
        final_frequency: float = 0.1,
        intrinsic_fitness: float = 1.0,
        drug_ic50_shifts: Optional[Dict[str, float]] = None,
        phenotype: str = "SENSITIVE",
    ) -> DBClonalFitnessLineage:
        """Add a clonal fitness lineage to a study."""
        lineage = DBClonalFitnessLineage(
            id=uuid.uuid4(),
            study_id=study_id,
            clone_name=clone_name,
            driver_mutations=driver_mutations,
            initial_frequency=initial_frequency,
            final_frequency=final_frequency,
            intrinsic_fitness=intrinsic_fitness,
            drug_ic50_shifts=drug_ic50_shifts or {},
            phenotype=phenotype,
        )
        self.session.add(lineage)
        await self.session.commit()
        await self.session.refresh(lineage)
        return lineage

    async def get_lineages_by_study(self, study_id: uuid.UUID) -> List[DBClonalFitnessLineage]:
        """Get all clonal lineages for a study."""
        stmt = select(DBClonalFitnessLineage).where(DBClonalFitnessLineage.study_id == study_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_trajectory_point(
        self,
        study_id: uuid.UUID,
        time_step: int,
        drug_concentration: float,
        tumor_burden: float,
        clone_abundances: Dict[str, float],
        resistance_index: float,
        adaptive_recommendation: Optional[str] = None,
    ) -> DBDrugResistanceTrajectory:
        """Add a time-point trajectory record to a study."""
        traj = DBDrugResistanceTrajectory(
            id=uuid.uuid4(),
            study_id=study_id,
            time_step=time_step,
            drug_concentration=drug_concentration,
            tumor_burden=tumor_burden,
            clone_abundances=clone_abundances,
            resistance_index=resistance_index,
            adaptive_recommendation=adaptive_recommendation,
        )
        self.session.add(traj)
        await self.session.commit()
        await self.session.refresh(traj)
        return traj

    async def get_trajectories_by_study(self, study_id: uuid.UUID) -> List[DBDrugResistanceTrajectory]:
        """Get all longitudinal trajectory points for a study."""
        stmt = (
            select(DBDrugResistanceTrajectory)
            .where(DBDrugResistanceTrajectory.study_id == study_id)
            .order_by(DBDrugResistanceTrajectory.time_step.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
