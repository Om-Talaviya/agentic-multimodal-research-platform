"""
Repository for Multi-Omics Pathway Perturbation & Signaling Simulation.
"""
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from database.models.pathway_perturbation import (
    DBMultiOmicsExperiment,
    DBPathwayCascade,
    DBPerturbationSimulation
)

class PathwayPerturbationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_experiment(
        self,
        title: str,
        cell_line: str = "A549",
        perturbation_type: str = "CRISPR_KO",
        omics_layers: Optional[List[str]] = None,
        user_id: Optional[uuid.UUID] = None
    ) -> DBMultiOmicsExperiment:
        exp = DBMultiOmicsExperiment(
            id=uuid.uuid4(),
            user_id=user_id,
            title=title,
            cell_line=cell_line,
            perturbation_type=perturbation_type,
            omics_layers=omics_layers or ["Transcriptomics", "Phospho-Proteomics", "Metabolomics"],
            status="SIMULATED"
        )
        self.session.add(exp)
        await self.session.commit()
        await self.session.refresh(exp)
        return exp

    async def get_experiment(self, exp_id: uuid.UUID) -> Optional[DBMultiOmicsExperiment]:
        query = (
            select(DBMultiOmicsExperiment)
            .options(
                selectinload(DBMultiOmicsExperiment.cascades),
                selectinload(DBMultiOmicsExperiment.simulations)
            )
            .where(DBMultiOmicsExperiment.id == exp_id)
        )
        res = await self.session.execute(query)
        return res.scalars().first()

    async def list_experiments(self, limit: int = 50) -> List[DBMultiOmicsExperiment]:
        query = select(DBMultiOmicsExperiment).order_by(DBMultiOmicsExperiment.created_at.desc()).limit(limit)
        res = await self.session.execute(query)
        return list(res.scalars().all())

    async def add_cascade(
        self,
        experiment_id: uuid.UUID,
        pathway_name: str,
        node_count: int,
        feedback_loops_count: int,
        steady_state_activation: float,
        cascade_topology: Dict[str, Any]
    ) -> DBPathwayCascade:
        cascade = DBPathwayCascade(
            id=uuid.uuid4(),
            experiment_id=experiment_id,
            pathway_name=pathway_name,
            node_count=node_count,
            feedback_loops_count=feedback_loops_count,
            steady_state_activation=steady_state_activation,
            cascade_topology=cascade_topology
        )
        self.session.add(cascade)
        await self.session.commit()
        await self.session.refresh(cascade)
        return cascade

    async def add_simulation(
        self,
        experiment_id: uuid.UUID,
        target_node: str,
        inhibition_efficiency: float,
        downstream_phospho_delta: float,
        metabolic_flux_shift: float,
        time_course_hours: int,
        time_series_trajectories: List[Dict[str, Any]],
        bypass_mechanisms: List[Dict[str, Any]]
    ) -> DBPerturbationSimulation:
        sim = DBPerturbationSimulation(
            id=uuid.uuid4(),
            experiment_id=experiment_id,
            target_node=target_node,
            inhibition_efficiency_pct=inhibition_efficiency,
            downstream_phospho_delta_pct=downstream_phospho_delta,
            metabolic_flux_shift_pct=metabolic_flux_shift,
            time_course_hours=time_course_hours,
            time_series_trajectories=time_series_trajectories,
            bypass_resistance_mechanisms=bypass_mechanisms
        )
        self.session.add(sim)
        await self.session.commit()
        await self.session.refresh(sim)
        return sim
