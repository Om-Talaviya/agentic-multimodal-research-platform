"""TCE Repo (Phase 113)."""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.tce_bispecific import DBTCEConstructDesign, DBSynapseGeometryMetric

class TCERepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_construct(self, workspace_id: uuid.UUID, construct_name: str,
                               tumor_target_antigen: str, tcell_effector_arm: str,
                               format_geometry: str, linker_length_amino_acids: int,
                               synapse_distance_angstroms: float, cytotoxicity_ec50_pm: float,
                               crs_safety_index: float) -> DBTCEConstructDesign:
        construct = DBTCEConstructDesign(
            workspace_id=workspace_id,
            construct_name=construct_name,
            tumor_target_antigen=tumor_target_antigen,
            tcell_effector_arm=tcell_effector_arm,
            format_geometry=format_geometry,
            linker_length_amino_acids=linker_length_amino_acids,
            synapse_distance_angstroms=synapse_distance_angstroms,
            cytotoxicity_ec50_pm=cytotoxicity_ec50_pm,
            crs_safety_index=crs_safety_index,
        )
        self.db.add(construct)
        await self.db.commit()
        await self.db.refresh(construct)
        return construct

    async def add_synapse_metric(self, construct_id: uuid.UUID, intermembrane_distance_nm: float,
                                 cd45_exclusion_efficiency: float,
                                 perforin_granzyme_flux_score: float) -> DBSynapseGeometryMetric:
        m = DBSynapseGeometryMetric(
            construct_id=construct_id,
            intermembrane_distance_nm=intermembrane_distance_nm,
            cd45_exclusion_efficiency=cd45_exclusion_efficiency,
            perforin_granzyme_flux_score=perforin_granzyme_flux_score,
        )
        self.db.add(m)
        await self.db.commit()
        await self.db.refresh(m)
        return m

    async def get_construct(self, construct_id: uuid.UUID) -> Optional[DBTCEConstructDesign]:
        res = await self.db.execute(select(DBTCEConstructDesign).where(DBTCEConstructDesign.id == construct_id))
        return res.scalar_one_or_none()
