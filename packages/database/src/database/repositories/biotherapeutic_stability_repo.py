from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from database.models.biotherapeutic_stability import (
    DBBiotherapeuticConstruct,
    DBHydrophobicPatch,
    DBFormulationExcipientScreen,
)

class BiotherapeuticStabilityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_construct(
        self,
        construct_name: str,
        modality: str,
        heavy_chain_sequence: str,
        light_chain_sequence: Optional[str] = None,
        melting_temp_tm1_celsius: float = 71.5,
        melting_temp_tm2_celsius: float = 82.4,
        aggregation_propensity_score: float = 0.18,
        colloidal_stability_kd: float = -5.2,
        diffusion_interaction_parameter_b22: float = 1.8e-4,
        shelf_life_months_at_4c: float = 24.0,
        properties: Optional[Dict[str, Any]] = None,
    ) -> DBBiotherapeuticConstruct:
        construct = DBBiotherapeuticConstruct(
            construct_name=construct_name,
            modality=modality,
            heavy_chain_sequence=heavy_chain_sequence,
            light_chain_sequence=light_chain_sequence,
            melting_temp_tm1_celsius=melting_temp_tm1_celsius,
            melting_temp_tm2_celsius=melting_temp_tm2_celsius,
            aggregation_propensity_score=aggregation_propensity_score,
            colloidal_stability_kd=colloidal_stability_kd,
            diffusion_interaction_parameter_b22=diffusion_interaction_parameter_b22,
            shelf_life_months_at_4c=shelf_life_months_at_4c,
            properties=properties or {},
        )
        self.session.add(construct)
        await self.session.commit()
        await self.session.refresh(construct)
        return construct

    async def add_hydrophobic_patch(
        self,
        construct_id: str,
        patch_identifier: str,
        surface_area_angstrom2: float,
        average_hydrophobicity_score: float,
        residue_span: str,
        aggregation_risk_level: str = "LOW",
    ) -> DBHydrophobicPatch:
        patch = DBHydrophobicPatch(
            construct_id=construct_id,
            patch_identifier=patch_identifier,
            surface_area_angstrom2=surface_area_angstrom2,
            average_hydrophobicity_score=average_hydrophobicity_score,
            residue_span=residue_span,
            aggregation_risk_level=aggregation_risk_level,
        )
        self.session.add(patch)
        await self.session.commit()
        await self.session.refresh(patch)
        return patch

    async def add_excipient_screen(
        self,
        construct_id: str,
        buffer_type: str = "Histidine",
        ph: float = 6.0,
        surfactant: str = "Polysorbate 80",
        tonicity_agent: str = "Sucrose",
        monomer_retention_pct_at_40c: float = 96.8,
    ) -> DBFormulationExcipientScreen:
        screen = DBFormulationExcipientScreen(
            construct_id=construct_id,
            buffer_type=buffer_type,
            ph=ph,
            surfactant=surfactant,
            tonicity_agent=tonicity_agent,
            monomer_retention_pct_at_40c=monomer_retention_pct_at_40c,
        )
        self.session.add(screen)
        await self.session.commit()
        await self.session.refresh(screen)
        return screen

    async def get_construct_by_id(self, construct_id: str) -> Optional[DBBiotherapeuticConstruct]:
        stmt = (
            select(DBBiotherapeuticConstruct)
            .options(
                selectinload(DBBiotherapeuticConstruct.hydrophobic_patches),
                selectinload(DBBiotherapeuticConstruct.excipient_screens),
            )
            .where(DBBiotherapeuticConstruct.id == construct_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_constructs(self, limit: int = 50) -> List[DBBiotherapeuticConstruct]:
        stmt = (
            select(DBBiotherapeuticConstruct)
            .options(
                selectinload(DBBiotherapeuticConstruct.hydrophobic_patches),
                selectinload(DBBiotherapeuticConstruct.excipient_screens),
            )
            .order_by(DBBiotherapeuticConstruct.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
