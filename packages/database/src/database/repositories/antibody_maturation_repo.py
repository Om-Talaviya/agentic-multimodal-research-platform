"""
Phase 127: Autonomous In-Silico Antibody Affinity Maturation & Somatic Hypermutation Repository.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
import uuid

from database.models.antibody_maturation import (
    DBAntibodyAffinityMaturation,
    DBDirectedEvolutionVariant,
    DBParatopeEpitopeContact,
)


class AntibodyMaturationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_campaign(
        self,
        candidate_name: str,
        target_antigen: str,
        parental_kd_nm: float = 12.4,
        matured_kd_nm: float = 0.18,
        affinity_fold_improvement: float = 68.8,
        humanness_score_oasis: float = 0.89,
        thermostability_tm_celsius: float = 74.5,
        evolution_rounds: int = 4,
        metadata_json: Optional[Dict[str, Any]] = None,
        project_id: Optional[str] = None,
    ) -> DBAntibodyAffinityMaturation:
        campaign = DBAntibodyAffinityMaturation(
            id=uuid.uuid4(),
            project_id=project_id,
            candidate_name=candidate_name,
            target_antigen=target_antigen,
            parental_kd_nm=parental_kd_nm,
            matured_kd_nm=matured_kd_nm,
            affinity_fold_improvement=affinity_fold_improvement,
            humanness_score_oasis=humanness_score_oasis,
            thermostability_tm_celsius=thermostability_tm_celsius,
            evolution_rounds=evolution_rounds,
            metadata_json=metadata_json or {},
        )
        self.session.add(campaign)
        await self.session.commit()
        await self.session.refresh(campaign)
        return campaign

    async def get_campaign(self, campaign_id: uuid.UUID) -> Optional[DBAntibodyAffinityMaturation]:
        stmt = (
            select(DBAntibodyAffinityMaturation)
            .options(
                selectinload(DBAntibodyAffinityMaturation.variants),
                selectinload(DBAntibodyAffinityMaturation.contacts),
            )
            .where(DBAntibodyAffinityMaturation.id == campaign_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_campaigns(self, limit: int = 50) -> List[DBAntibodyAffinityMaturation]:
        stmt = (
            select(DBAntibodyAffinityMaturation)
            .options(
                selectinload(DBAntibodyAffinityMaturation.variants),
                selectinload(DBAntibodyAffinityMaturation.contacts),
            )
            .order_by(desc(DBAntibodyAffinityMaturation.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_variant(
        self,
        campaign_id: uuid.UUID,
        variant_id: str,
        cdr_region: str,
        mutations_summary: str,
        predicted_binding_energy_ddg: float = -2.45,
        dissociation_constant_kd_nm: float = 0.22,
        developability_flag: bool = True,
        polyreactivity_risk: float = 0.04,
    ) -> DBDirectedEvolutionVariant:
        variant = DBDirectedEvolutionVariant(
            id=uuid.uuid4(),
            campaign_id=campaign_id,
            variant_id=variant_id,
            cdr_region=cdr_region,
            mutations_summary=mutations_summary,
            predicted_binding_energy_ddg=predicted_binding_energy_ddg,
            dissociation_constant_kd_nm=dissociation_constant_kd_nm,
            developability_flag=developability_flag,
            polyreactivity_risk=polyreactivity_risk,
        )
        self.session.add(variant)
        await self.session.commit()
        await self.session.refresh(variant)
        return variant

    async def add_contact(
        self,
        campaign_id: uuid.UUID,
        antibody_residue: str,
        antigen_residue: str,
        interaction_type: str,
        interaction_distance_angstrom: float = 2.85,
        binding_energy_contribution_kcal: float = -1.65,
    ) -> DBParatopeEpitopeContact:
        contact = DBParatopeEpitopeContact(
            id=uuid.uuid4(),
            campaign_id=campaign_id,
            antibody_residue=antibody_residue,
            antigen_residue=antigen_residue,
            interaction_type=interaction_type,
            interaction_distance_angstrom=interaction_distance_angstrom,
            binding_energy_contribution_kcal=binding_energy_contribution_kcal,
        )
        self.session.add(contact)
        await self.session.commit()
        await self.session.refresh(contact)
        return contact
