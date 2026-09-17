"""Repository for Synthetic Cell Membrane Dynamics & LNP Formulation."""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database.models.lnp_formulation import (
    DBLNPFormulationStudy,
    DBLNPLipidComponent,
    DBMembraneDynamicsProfile,
)


class LNPFormulationRepository:
    """Handles async database operations for LNP formulation and membrane dynamics."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_formulation(
        self,
        formulation_name: str,
        cargo_type: str = "mRNA",
        ionizable_lipid_name: str = "ALC-0315",
        lipid_ratio_molar_json: Optional[Dict[str, float]] = None,
        np_ratio: float = 6.0,
        encapsulation_efficiency_pct: float = 94.5,
        mean_diameter_nm: float = 78.2,
        pdi_polydispersity_index: float = 0.12,
        zeta_potential_mv: float = 2.4,
        apparent_pka: float = 6.45,
        simulation_metadata_json: Optional[Dict[str, Any]] = None,
    ) -> DBLNPFormulationStudy:
        study = DBLNPFormulationStudy(
            formulation_name=formulation_name,
            cargo_type=cargo_type,
            ionizable_lipid_name=ionizable_lipid_name,
            lipid_ratio_molar_json=lipid_ratio_molar_json or {"ionizable": 50.0, "helper": 10.0, "cholesterol": 38.5, "peg": 1.5},
            np_ratio=np_ratio,
            encapsulation_efficiency_pct=encapsulation_efficiency_pct,
            mean_diameter_nm=mean_diameter_nm,
            pdi_polydispersity_index=pdi_polydispersity_index,
            zeta_potential_mv=zeta_potential_mv,
            apparent_pka=apparent_pka,
            simulation_metadata_json=simulation_metadata_json or {},
        )
        self.session.add(study)
        await self.session.commit()
        await self.session.refresh(study)
        return study

    async def get_formulation(self, formulation_id: str) -> Optional[DBLNPFormulationStudy]:
        stmt = select(DBLNPFormulationStudy).where(DBLNPFormulationStudy.id == formulation_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_formulations(self, limit: int = 50, offset: int = 0) -> List[DBLNPFormulationStudy]:
        stmt = select(DBLNPFormulationStudy).order_by(desc(DBLNPFormulationStudy.created_at)).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_components(
        self,
        formulation_id: str,
        components_data: List[Dict[str, Any]],
    ) -> List[DBLNPLipidComponent]:
        created = []
        for c in components_data:
            item = DBLNPLipidComponent(
                formulation_id=formulation_id,
                component_name=c["component_name"],
                lipid_category=c["lipid_category"],
                molar_percentage=c.get("molar_percentage", 25.0),
                molecular_weight_g_mol=c.get("molecular_weight_g_mol", 700.0),
                charge_at_ph7=c.get("charge_at_ph7", 0.0),
            )
            self.session.add(item)
            created.append(item)
        await self.session.commit()
        for item in created:
            await self.session.refresh(item)
        return created

    async def get_components_by_formulation(self, formulation_id: str) -> List[DBLNPLipidComponent]:
        stmt = select(DBLNPLipidComponent).where(DBLNPLipidComponent.formulation_id == formulation_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_membrane_profile(
        self,
        formulation_id: str,
        profile_data: Dict[str, Any],
    ) -> DBMembraneDynamicsProfile:
        item = DBMembraneDynamicsProfile(
            formulation_id=formulation_id,
            membrane_thickness_angstrom=profile_data.get("membrane_thickness_angstrom", 39.5),
            area_per_lipid_angstrom2=profile_data.get("area_per_lipid_angstrom2", 62.4),
            order_parameter_s2=profile_data.get("order_parameter_s2", 0.22),
            bending_modulus_kc_kbt=profile_data.get("bending_modulus_kc_kbt", 24.5),
            endosomal_escape_efficiency_pct=profile_data.get("endosomal_escape_efficiency_pct", 18.5),
            cytotoxicity_score=profile_data.get("cytotoxicity_score", 0.15),
        )
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def get_membrane_profile_by_formulation(self, formulation_id: str) -> Optional[DBMembraneDynamicsProfile]:
        stmt = select(DBMembraneDynamicsProfile).where(DBMembraneDynamicsProfile.formulation_id == formulation_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
