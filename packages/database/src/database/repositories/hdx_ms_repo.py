"""
Repository for Phase 105: HDX-MS Conformational Dynamics.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
import uuid

from database.models.hdx_ms import DBHDXExperiment, DBDeuteriumUptakeCurve, DBProtectionFactorMap

class HDXMassSpecRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_experiment(
        self,
        protein_name: str,
        user_id: Optional[uuid.UUID] = None,
        uniprot_id: Optional[str] = None,
        state_condition: str = "APO",
        sequence_coverage_pct: float = 0.0,
        redundancy_score: float = 0.0,
        deuteration_buffer_ph: float = 7.4,
        temperature_celsius: float = 20.0,
        metadata_json: Optional[Dict[str, Any]] = None,
    ) -> DBHDXExperiment:
        exp = DBHDXExperiment(
            id=uuid.uuid4(),
            user_id=user_id,
            protein_name=protein_name,
            uniprot_id=uniprot_id,
            state_condition=state_condition,
            sequence_coverage_pct=sequence_coverage_pct,
            redundancy_score=redundancy_score,
            deuteration_buffer_ph=deuteration_buffer_ph,
            temperature_celsius=temperature_celsius,
            metadata_json=metadata_json or {},
            status="COMPLETED"
        )
        self.session.add(exp)
        await self.session.commit()
        await self.session.refresh(exp)
        return exp

    async def get_experiment(self, experiment_id: uuid.UUID) -> Optional[DBHDXExperiment]:
        stmt = (
            select(DBHDXExperiment)
            .options(selectinload(DBHDXExperiment.uptake_curves), selectinload(DBHDXExperiment.protection_maps))
            .where(DBHDXExperiment.id == experiment_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_experiments(self, limit: int = 50, offset: int = 0) -> List[DBHDXExperiment]:
        stmt = (
            select(DBHDXExperiment)
            .order_by(desc(DBHDXExperiment.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_uptake_curves(
        self,
        experiment_id: uuid.UUID,
        curves_data: List[Dict[str, Any]]
    ) -> List[DBDeuteriumUptakeCurve]:
        entities = []
        for c in curves_data:
            entity = DBDeuteriumUptakeCurve(
                id=uuid.uuid4(),
                experiment_id=experiment_id,
                peptide_sequence=c["peptide_sequence"],
                start_res=c["start_res"],
                end_res=c["end_res"],
                timepoint_seconds=c["timepoint_seconds"],
                deuterium_uptake_da=c.get("deuterium_uptake_da", 0.0),
                fractional_uptake_pct=c.get("fractional_uptake_pct", 0.0),
                protection_factor_ln_p=c.get("protection_factor_ln_p", 0.0)
            )
            entities.append(entity)
            self.session.add(entity)

        exp = await self.session.get(DBHDXExperiment, experiment_id)
        if exp:
            unique_peptides = {c["peptide_sequence"] for c in curves_data}
            exp.total_peptides = len(unique_peptides)

        await self.session.commit()
        return entities

    async def add_protection_maps(
        self,
        experiment_id: uuid.UUID,
        maps_data: List[Dict[str, Any]]
    ) -> List[DBProtectionFactorMap]:
        entities = []
        for m in maps_data:
            entity = DBProtectionFactorMap(
                id=uuid.uuid4(),
                experiment_id=experiment_id,
                residue_number=m["residue_number"],
                amino_acid=m["amino_acid"],
                protection_factor=m.get("protection_factor", 1.0),
                solvent_accessibility_level=m.get("solvent_accessibility_level", "EXPOSED"),
                delta_uptake_apo_vs_bound=m.get("delta_uptake_apo_vs_bound", 0.0)
            )
            entities.append(entity)
            self.session.add(entity)
        await self.session.commit()
        return entities
