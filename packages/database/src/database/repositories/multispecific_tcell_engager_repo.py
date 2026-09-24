"""Repository for Multispecific T-Cell Engager (Phase 158)."""

import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.multispecific_tcell_engager import (
    DBMultispecificTCellEngagerStudy,
    DBTargetBindingDomainGeometry,
    DBSynapticDistanceProfile,
)


class MultispecificTCellEngagerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_study(
        self,
        construct_name: str,
        modality_format: str,
        primary_tumor_antigen: str,
        tcell_activation_arm: str,
        synaptic_cleft_distance_a: float,
        cytolytic_potency_ec50_pm: float,
        perforin_granzyme_flux: float,
        crs_cytokine_risk_score: float,
    ) -> DBMultispecificTCellEngagerStudy:
        study = DBMultispecificTCellEngagerStudy(
            id=uuid.uuid4(),
            construct_name=construct_name,
            modality_format=modality_format,
            primary_tumor_antigen=primary_tumor_antigen,
            tcell_activation_arm=tcell_activation_arm,
            synaptic_cleft_distance_a=synaptic_cleft_distance_a,
            cytolytic_potency_ec50_pm=cytolytic_potency_ec50_pm,
            perforin_granzyme_flux=perforin_granzyme_flux,
            crs_cytokine_risk_score=crs_cytokine_risk_score,
        )
        self.db.add(study)
        await self.db.commit()
        await self.db.refresh(study)
        return study

    async def add_binding_domain(
        self,
        study_id: uuid.UUID,
        arm_designation: str,
        target_epitope: str,
        kd_affinity_nM: float,
        arm_length_angstrom: float,
        rotational_flexibility_deg: float,
    ) -> DBTargetBindingDomainGeometry:
        rec = DBTargetBindingDomainGeometry(
            id=uuid.uuid4(),
            study_id=study_id,
            arm_designation=arm_designation,
            target_epitope=target_epitope,
            kd_affinity_nM=kd_affinity_nM,
            arm_length_angstrom=arm_length_angstrom,
            rotational_flexibility_deg=rotational_flexibility_deg,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def add_synapse_profile(
        self,
        study_id: uuid.UUID,
        intermembrane_distance_nm: float,
        synapse_maturation_time_min: float,
        lytic_granule_polarization_pct: float,
        tumor_lysis_percentage: float,
    ) -> DBSynapticDistanceProfile:
        rec = DBSynapticDistanceProfile(
            id=uuid.uuid4(),
            study_id=study_id,
            intermembrane_distance_nm=intermembrane_distance_nm,
            synapse_maturation_time_min=synapse_maturation_time_min,
            lytic_granule_polarization_pct=lytic_granule_polarization_pct,
            tumor_lysis_percentage=tumor_lysis_percentage,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def get_study_with_details(self, study_id: uuid.UUID) -> Optional[DBMultispecificTCellEngagerStudy]:
        stmt = (
            select(DBMultispecificTCellEngagerStudy)
            .where(DBMultispecificTCellEngagerStudy.id == study_id)
            .options(
                selectinload(DBMultispecificTCellEngagerStudy.binding_domains),
                selectinload(DBMultispecificTCellEngagerStudy.synapse_profiles),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
