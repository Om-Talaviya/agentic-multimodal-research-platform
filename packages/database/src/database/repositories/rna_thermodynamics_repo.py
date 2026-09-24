"""
Repository for Phase 163: RNA Thermodynamics & MFE Folding.
"""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.rna_thermodynamics import (
    DBRNAThermodynamicsStudy,
    DBRNABasePairProbability,
    DBRNAPseudoknotStructure,
)


class RNAThermodynamicsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_study(
        self,
        rna_name: str,
        sequence: str,
        sequence_length: int,
        dot_bracket_structure: str,
        mfe_delta_g_kcal_mol: float,
        ensemble_free_energy_kcal_mol: float,
        ensemble_defect_score: float = 0.0,
        melting_temperature_tm_celsius: float = 0.0,
        thermodynamic_ruleset: str = "Turner-2004-NearestNeighbor",
        project_id: Optional[uuid.UUID] = None,
    ) -> DBRNAThermodynamicsStudy:
        study = DBRNAThermodynamicsStudy(
            rna_name=rna_name,
            sequence=sequence,
            sequence_length=sequence_length,
            dot_bracket_structure=dot_bracket_structure,
            mfe_delta_g_kcal_mol=mfe_delta_g_kcal_mol,
            ensemble_free_energy_kcal_mol=ensemble_free_energy_kcal_mol,
            ensemble_defect_score=ensemble_defect_score,
            melting_temperature_tm_celsius=melting_temperature_tm_celsius,
            thermodynamic_ruleset=thermodynamic_ruleset,
            project_id=project_id,
        )
        self.db.add(study)
        await self.db.commit()
        await self.db.refresh(study)
        return study

    async def add_base_pair_probability(
        self,
        study_id: uuid.UUID,
        pos_i: int,
        pos_j: int,
        pairing_probability: float,
        base_pair_type: str = "Watson-Crick",
    ) -> DBRNABasePairProbability:
        bp = DBRNABasePairProbability(
            study_id=study_id,
            pos_i=pos_i,
            pos_j=pos_j,
            pairing_probability=pairing_probability,
            base_pair_type=base_pair_type,
        )
        self.db.add(bp)
        await self.db.commit()
        await self.db.refresh(bp)
        return bp

    async def add_pseudoknot(
        self,
        study_id: uuid.UUID,
        stem1_range: str,
        stem2_range: str,
        loop_topology: str = "H-type Pseudoknot",
        pseudoknot_stability_delta_g_kcal_mol: float = 0.0,
    ) -> DBRNAPseudoknotStructure:
        pk = DBRNAPseudoknotStructure(
            study_id=study_id,
            stem1_range=stem1_range,
            stem2_range=stem2_range,
            loop_topology=loop_topology,
            pseudoknot_stability_delta_g_kcal_mol=pseudoknot_stability_delta_g_kcal_mol,
        )
        self.db.add(pk)
        await self.db.commit()
        await self.db.refresh(pk)
        return pk

    async def get_study(self, study_id: uuid.UUID) -> Optional[DBRNAThermodynamicsStudy]:
        stmt = (
            select(DBRNAThermodynamicsStudy)
            .options(
                selectinload(DBRNAThermodynamicsStudy.base_pairs),
                selectinload(DBRNAThermodynamicsStudy.pseudoknots),
            )
            .where(DBRNAThermodynamicsStudy.id == study_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()
