"""
Repository for Phase 132: Global Pandemic Biosurveillance & Multi-Strain Viral Lineage Phylodynamics.
"""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from database.models.viral_phylodynamics import (
    DBViralSurveillanceStudy,
    DBPhylodynamicLineage,
    DBStrainTransmissionFitness,
)


class ViralPhylodynamicsRepository:
    """Repository handling CRUD operations for viral phylodynamic studies and lineage clades."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        pathogen_name: str,
        genome_type: str = "ssRNA(+)",
        geographic_regions: Optional[List[str]] = None,
        total_genomes_sequenced: int = 50000,
        effective_reproduction_number_rt: float = 1.35,
        transmission_fitness_gain_pct: float = 24.5,
        metadata_json: Optional[Dict[str, Any]] = None,
        project_id: Optional[str] = None,
    ) -> DBViralSurveillanceStudy:
        """Create a new viral genomic biosurveillance study."""
        study = DBViralSurveillanceStudy(
            id=uuid.uuid4(),
            project_id=project_id,
            pathogen_name=pathogen_name,
            genome_type=genome_type,
            geographic_regions=geographic_regions or ["Global", "North America", "Europe", "Asia"],
            total_genomes_sequenced=total_genomes_sequenced,
            effective_reproduction_number_rt=effective_reproduction_number_rt,
            transmission_fitness_gain_pct=transmission_fitness_gain_pct,
            metadata_json=metadata_json or {},
        )
        self.session.add(study)
        await self.session.commit()
        await self.session.refresh(study)
        return study

    async def get_study(self, study_id: uuid.UUID) -> Optional[DBViralSurveillanceStudy]:
        """Get study with lineages and fitness profiles."""
        stmt = (
            select(DBViralSurveillanceStudy)
            .options(
                selectinload(DBViralSurveillanceStudy.lineages),
                selectinload(DBViralSurveillanceStudy.fitness_profiles),
            )
            .where(DBViralSurveillanceStudy.id == study_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DBViralSurveillanceStudy]:
        """List all viral biosurveillance studies."""
        stmt = (
            select(DBViralSurveillanceStudy)
            .order_by(desc(DBViralSurveillanceStudy.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_lineage(
        self,
        study_id: uuid.UUID,
        lineage_clade: str,
        pangolin_designation: str,
        defining_mutations: List[str],
        who_label: Optional[str] = None,
        growth_advantage_daily: float = 0.08,
        immune_evasion_score: float = 0.88,
        global_prevalence_pct: float = 42.5,
    ) -> DBPhylodynamicLineage:
        """Add a phylodynamic lineage to a study."""
        lineage = DBPhylodynamicLineage(
            id=uuid.uuid4(),
            study_id=study_id,
            lineage_clade=lineage_clade,
            pangolin_designation=pangolin_designation,
            who_label=who_label,
            defining_mutations=defining_mutations,
            growth_advantage_daily=growth_advantage_daily,
            immune_evasion_score=immune_evasion_score,
            global_prevalence_pct=global_prevalence_pct,
        )
        self.session.add(lineage)
        await self.session.commit()
        await self.session.refresh(lineage)
        return lineage

    async def add_fitness_profile(
        self,
        study_id: uuid.UUID,
        clade_name: str,
        basic_reproduction_number_r0: float = 3.2,
        serial_interval_days: float = 3.8,
        ace2_binding_affinity_shift: float = 1.45,
        cross_neutralization_titer_fold_drop: float = 12.5,
    ) -> DBStrainTransmissionFitness:
        """Add transmission fitness data for a clade."""
        profile = DBStrainTransmissionFitness(
            id=uuid.uuid4(),
            study_id=study_id,
            clade_name=clade_name,
            basic_reproduction_number_r0=basic_reproduction_number_r0,
            serial_interval_days=serial_interval_days,
            ace2_binding_affinity_shift=ace2_binding_affinity_shift,
            cross_neutralization_titer_fold_drop=cross_neutralization_titer_fold_drop,
        )
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile
