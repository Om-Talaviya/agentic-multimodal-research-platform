"""Repository for Chemogenomics Polypharmacology & Off-Target Interactome."""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database.models.chemogenomics_polypharmacology import (
    DBCompoundPolypharmacologyProfile,
    DBTargetBindingAffinity,
    DBOffTargetToxicityAlert,
)


class ChemogenomicsRepository:
    """Handles async database operations for chemogenomics polypharmacology."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_profile(
        self,
        compound_name: str,
        smiles: str,
        primary_target: str,
        gini_selectivity_index: float,
        selectivity_tier: str = "FAMILY_SELECTIVE",
        total_targets_screened: int = 50,
        off_target_liabilities_count: int = 0,
        profile_summary_json: Optional[Dict[str, Any]] = None,
    ) -> DBCompoundPolypharmacologyProfile:
        profile = DBCompoundPolypharmacologyProfile(
            compound_name=compound_name,
            smiles=smiles,
            primary_target=primary_target,
            gini_selectivity_index=gini_selectivity_index,
            selectivity_tier=selectivity_tier,
            total_targets_screened=total_targets_screened,
            off_target_liabilities_count=off_target_liabilities_count,
            profile_summary_json=profile_summary_json or {},
        )
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def get_profile(self, profile_id: str) -> Optional[DBCompoundPolypharmacologyProfile]:
        stmt = select(DBCompoundPolypharmacologyProfile).where(DBCompoundPolypharmacologyProfile.id == profile_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_profiles(self, limit: int = 50, offset: int = 0) -> List[DBCompoundPolypharmacologyProfile]:
        stmt = select(DBCompoundPolypharmacologyProfile).order_by(desc(DBCompoundPolypharmacologyProfile.created_at)).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_affinities(
        self,
        profile_id: str,
        affinities_data: List[Dict[str, Any]],
    ) -> List[DBTargetBindingAffinity]:
        created = []
        for a in affinities_data:
            item = DBTargetBindingAffinity(
                profile_id=profile_id,
                target_gene=a["target_gene"],
                uniprot_id=a["uniprot_id"],
                protein_family=a.get("protein_family", "KINASE"),
                affinity_type=a.get("affinity_type", "IC50"),
                affinity_value_nm=a["affinity_value_nm"],
                is_primary_target=a.get("is_primary_target", False),
                is_off_target_liability=a.get("is_off_target_liability", False),
            )
            self.session.add(item)
            created.append(item)
        await self.session.commit()
        for item in created:
            await self.session.refresh(item)
        return created

    async def get_affinities_by_profile(self, profile_id: str) -> List[DBTargetBindingAffinity]:
        stmt = select(DBTargetBindingAffinity).where(DBTargetBindingAffinity.profile_id == profile_id).order_by(DBTargetBindingAffinity.affinity_value_nm)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_alerts(
        self,
        profile_id: str,
        alerts_data: List[Dict[str, Any]],
    ) -> List[DBOffTargetToxicityAlert]:
        created = []
        for alert in alerts_data:
            item = DBOffTargetToxicityAlert(
                profile_id=profile_id,
                target_gene=alert["target_gene"],
                risk_type=alert["risk_type"],
                binding_potency_nm=alert["binding_potency_nm"],
                severity=alert.get("severity", "HIGH"),
                recommendation=alert.get("recommendation", ""),
            )
            self.session.add(item)
            created.append(item)
        await self.session.commit()
        for item in created:
            await self.session.refresh(item)
        return created

    async def get_alerts_by_profile(self, profile_id: str) -> List[DBOffTargetToxicityAlert]:
        stmt = select(DBOffTargetToxicityAlert).where(DBOffTargetToxicityAlert.profile_id == profile_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
