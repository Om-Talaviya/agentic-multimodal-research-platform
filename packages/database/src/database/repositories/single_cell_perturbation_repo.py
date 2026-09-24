"""
Repository for Phase 167: Single-Cell Perturbation & Causal GRN Inversion.
"""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.single_cell_perturbation import (
    DBSingleCellPerturbationStudy,
    DBPerturbationTargetEffect,
    DBCausalGRNEdge,
)


class SingleCellPerturbationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_study(
        self,
        study_name: str,
        perturbation_modality: str,
        total_cells_profiled: int,
        target_genes_count: int,
        energy_distance_shift: float,
        causal_network_density: float = 0.0,
        project_id: Optional[uuid.UUID] = None,
    ) -> DBSingleCellPerturbationStudy:
        study = DBSingleCellPerturbationStudy(
            study_name=study_name,
            perturbation_modality=perturbation_modality,
            total_cells_profiled=total_cells_profiled,
            target_genes_count=target_genes_count,
            energy_distance_shift=energy_distance_shift,
            causal_network_density=causal_network_density,
            project_id=project_id,
        )
        self.db.add(study)
        await self.db.commit()
        await self.db.refresh(study)
        return study

    async def add_target_effect(
        self,
        study_id: uuid.UUID,
        guide_target_gene: str,
        knockdown_efficiency_percent: float,
        differentially_expressed_genes_count: int,
        phenotypic_dispersion_score: float,
    ) -> DBPerturbationTargetEffect:
        effect = DBPerturbationTargetEffect(
            study_id=study_id,
            guide_target_gene=guide_target_gene,
            knockdown_efficiency_percent=knockdown_efficiency_percent,
            differentially_expressed_genes_count=differentially_expressed_genes_count,
            phenotypic_dispersion_score=phenotypic_dispersion_score,
        )
        self.db.add(effect)
        await self.db.commit()
        await self.db.refresh(effect)
        return effect

    async def add_grn_edge(
        self,
        study_id: uuid.UUID,
        source_regulator_gene: str,
        target_effector_gene: str,
        causal_weight_beta: float,
        p_value_fdr: float,
        regulation_sign: str = "Activation",
    ) -> DBCausalGRNEdge:
        edge = DBCausalGRNEdge(
            study_id=study_id,
            source_regulator_gene=source_regulator_gene,
            target_effector_gene=target_effector_gene,
            causal_weight_beta=causal_weight_beta,
            p_value_fdr=p_value_fdr,
            regulation_sign=regulation_sign,
        )
        self.db.add(edge)
        await self.db.commit()
        await self.db.refresh(edge)
        return edge

    async def get_study(self, study_id: uuid.UUID) -> Optional[DBSingleCellPerturbationStudy]:
        stmt = (
            select(DBSingleCellPerturbationStudy)
            .options(
                selectinload(DBSingleCellPerturbationStudy.target_effects),
                selectinload(DBSingleCellPerturbationStudy.grn_edges),
            )
            .where(DBSingleCellPerturbationStudy.id == study_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()
