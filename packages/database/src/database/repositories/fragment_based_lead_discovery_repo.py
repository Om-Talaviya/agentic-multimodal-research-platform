"""Repository for Phase 184: Fragment-Based Lead Discovery & Linker Growth."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.fragment_based_lead_discovery import FBDDLeadDiscoveryStudy, FBDDFragmentHit, FBDDLinkerGrowthCandidate


class FBDDLeadDiscoveryRepository:
    """Database operations for fragment-based drug discovery studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_protein_pocket: str,
        fragment_library_size: int = 1500,
        top_fragment_kd_micromolar: float = 42.5,
        mean_ligand_efficiency: float = 0.38,
        linker_growth_strategy: str = "fragment_linking_rigid",
        optimized_lead_predicted_pic50: float = 8.45,
        lipinski_rule_of_three_compliance_pct: float = 94.5,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> FBDDLeadDiscoveryStudy:
        study = FBDDLeadDiscoveryStudy(
            name=name,
            target_protein_pocket=target_protein_pocket,
            fragment_library_size=fragment_library_size,
            top_fragment_kd_micromolar=top_fragment_kd_micromolar,
            mean_ligand_efficiency=mean_ligand_efficiency,
            linker_growth_strategy=linker_growth_strategy,
            optimized_lead_predicted_pic50=optimized_lead_predicted_pic50,
            lipinski_rule_of_three_compliance_pct=lipinski_rule_of_three_compliance_pct,
            status=status,
            parameters=parameters or {},
            summary_report=summary_report,
        )
        self.session.add(study)
        await self.session.flush()
        await self.session.refresh(study)
        return study

    async def add_fragment_hit(
        self,
        study_id: UUID,
        fragment_id: str,
        smiles_representation: str,
        heavy_atom_count: int,
        molecular_weight_da: float,
        dissociation_constant_kd_um: float,
        ligand_efficiency_le: float,
        subpocket_binding_site: str = "Pocket-A",
    ) -> FBDDFragmentHit:
        item = FBDDFragmentHit(
            study_id=study_id,
            fragment_id=fragment_id,
            smiles_representation=smiles_representation,
            heavy_atom_count=heavy_atom_count,
            molecular_weight_da=molecular_weight_da,
            dissociation_constant_kd_um=dissociation_constant_kd_um,
            ligand_efficiency_le=ligand_efficiency_le,
            subpocket_binding_site=subpocket_binding_site,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def add_linker_candidate(
        self,
        study_id: UUID,
        lead_id: str,
        combined_smiles: str,
        linker_type: str,
        predicted_affinity_kd_nm: float,
        binding_delta_g_kcal_mol: float,
        synthetic_accessibility_sa_score: float,
    ) -> FBDDLinkerGrowthCandidate:
        item = FBDDLinkerGrowthCandidate(
            study_id=study_id,
            lead_id=lead_id,
            combined_smiles=combined_smiles,
            linker_type=linker_type,
            predicted_affinity_kd_nm=predicted_affinity_kd_nm,
            binding_delta_g_kcal_mol=binding_delta_g_kcal_mol,
            synthetic_accessibility_sa_score=synthetic_accessibility_sa_score,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_study(self, study_id: UUID) -> Optional[FBDDLeadDiscoveryStudy]:
        stmt = select(FBDDLeadDiscoveryStudy).where(FBDDLeadDiscoveryStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[FBDDLeadDiscoveryStudy]:
        stmt = select(FBDDLeadDiscoveryStudy).order_by(FBDDLeadDiscoveryStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())