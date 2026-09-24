"""Repository for Single-Cell Spatial Flux Balance (Phase 150)."""

import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.single_cell_spatial_flux import (
    DBSingleCellSpatialFluxStudy,
    DBMetabolicReactionFluxRate,
    DBTissueMicrodomainProfile,
)


class SpatialFluxRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_study(
        self,
        tissue_sample_id: str,
        organ_context: str,
        single_cells_simulated: int,
        mean_glycolytic_flux: float,
        mean_oxphos_flux: float,
        lactate_secretion_rate: float,
        atp_generation_rate: float,
    ) -> DBSingleCellSpatialFluxStudy:
        study = DBSingleCellSpatialFluxStudy(
            id=uuid.uuid4(),
            tissue_sample_id=tissue_sample_id,
            organ_context=organ_context,
            single_cells_simulated=single_cells_simulated,
            mean_glycolytic_flux=mean_glycolytic_flux,
            mean_oxphos_flux=mean_oxphos_flux,
            lactate_secretion_rate=lactate_secretion_rate,
            atp_generation_rate=atp_generation_rate,
        )
        self.db.add(study)
        await self.db.commit()
        await self.db.refresh(study)
        return study

    async def add_flux_rate(
        self,
        study_id: uuid.UUID,
        reaction_id: str,
        reaction_name: str,
        subsystem: str,
        flux_rate_mmol_gdw_h: float,
        shadow_price: float,
    ) -> DBMetabolicReactionFluxRate:
        rec = DBMetabolicReactionFluxRate(
            id=uuid.uuid4(),
            study_id=study_id,
            reaction_id=reaction_id,
            reaction_name=reaction_name,
            subsystem=subsystem,
            flux_rate_mmol_gdw_h=flux_rate_mmol_gdw_h,
            shadow_price=shadow_price,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def add_microdomain(
        self,
        study_id: uuid.UUID,
        domain_name: str,
        radial_distance_um: float,
        oxygen_concentration_uM: float,
        glucose_concentration_mM: float,
        warburg_phenotype_score: float,
    ) -> DBTissueMicrodomainProfile:
        rec = DBTissueMicrodomainProfile(
            id=uuid.uuid4(),
            study_id=study_id,
            domain_name=domain_name,
            radial_distance_um=radial_distance_um,
            oxygen_concentration_uM=oxygen_concentration_uM,
            glucose_concentration_mM=glucose_concentration_mM,
            warburg_phenotype_score=warburg_phenotype_score,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def get_study_with_details(self, study_id: uuid.UUID) -> Optional[DBSingleCellSpatialFluxStudy]:
        stmt = (
            select(DBSingleCellSpatialFluxStudy)
            .where(DBSingleCellSpatialFluxStudy.id == study_id)
            .options(
                selectinload(DBSingleCellSpatialFluxStudy.flux_rates),
                selectinload(DBSingleCellSpatialFluxStudy.microdomains),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
