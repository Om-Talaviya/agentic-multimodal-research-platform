"""Repository for Mitochondrial Bioenergetics (Phase 144)."""

import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.models.mitochondrial_bioenergetics import (
    DBMitochondrialOXPHOSStudy,
    DBETCComplexActivityRecord,
    DBROSDynamicsProfile,
)


class MitochondrialBioenergeticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_study(
        self,
        cell_line_or_tissue: str,
        oxygen_consumption_rate_pmol_min: float,
        extracellular_acidification_rate: float,
        respiratory_control_ratio: float,
        membrane_potential_delta_psi_mv: float,
    ) -> DBMitochondrialOXPHOSStudy:
        study = DBMitochondrialOXPHOSStudy(
            cell_line_or_tissue=cell_line_or_tissue,
            oxygen_consumption_rate_pmol_min=oxygen_consumption_rate_pmol_min,
            extracellular_acidification_rate=extracellular_acidification_rate,
            respiratory_control_ratio=respiratory_control_ratio,
            membrane_potential_delta_psi_mv=membrane_potential_delta_psi_mv,
        )
        self.db.add(study)
        await self.db.commit()
        await self.db.refresh(study)
        return study

    async def add_complex_record(
        self,
        study_id: uuid.UUID,
        complex_name: str,
        relative_activity_pct: float,
        proton_pumping_stoichiometry: float,
        inhibitor_sensitivity: str,
    ) -> DBETCComplexActivityRecord:
        rec = DBETCComplexActivityRecord(
            study_id=study_id,
            complex_name=complex_name,
            relative_activity_pct=relative_activity_pct,
            proton_pumping_stoichiometry=proton_pumping_stoichiometry,
            inhibitor_sensitivity=inhibitor_sensitivity,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def add_ros_profile(
        self,
        study_id: uuid.UUID,
        superoxide_flux_uM_s: float,
        h2o2_emission_rate: float,
        mptp_opening_probability: float,
        glutathione_redox_ratio: float,
    ) -> DBROSDynamicsProfile:
        prof = DBROSDynamicsProfile(
            study_id=study_id,
            superoxide_flux_uM_s=superoxide_flux_uM_s,
            h2o2_emission_rate=h2o2_emission_rate,
            mptp_opening_probability=mptp_opening_probability,
            glutathione_redox_ratio=glutathione_redox_ratio,
        )
        self.db.add(prof)
        await self.db.commit()
        await self.db.refresh(prof)
        return prof

    async def get_study_with_details(self, study_id: uuid.UUID) -> Optional[DBMitochondrialOXPHOSStudy]:
        stmt = (
            select(DBMitochondrialOXPHOSStudy)
            .where(DBMitochondrialOXPHOSStudy.id == study_id)
            .options(
                selectinload(DBMitochondrialOXPHOSStudy.etc_complexes),
                selectinload(DBMitochondrialOXPHOSStudy.ros_profiles),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
