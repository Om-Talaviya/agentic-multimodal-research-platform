"""Repository for Single-Molecule FRET (smFRET) Kinetics."""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database.models.smfret_kinetics import (
    DBSmFRETExperiment,
    DBSmFRETMoleculeTrace,
    DBConformationalState,
)


class SmFRETRepository:
    """Handles async database operations for single-molecule FRET kinetics."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_experiment(
        self,
        experiment_title: str,
        macromolecule_name: str,
        donor_fluorophore: str = "Cy3",
        acceptor_fluorophore: str = "Cy5",
        forster_radius_angstrom: float = 54.0,
        acquisition_rate_hz: float = 100.0,
        total_molecules_recorded: int = 1,
        state_count: int = 3,
        experiment_metadata_json: Optional[Dict[str, Any]] = None,
    ) -> DBSmFRETExperiment:
        exp = DBSmFRETExperiment(
            experiment_title=experiment_title,
            macromolecule_name=macromolecule_name,
            donor_fluorophore=donor_fluorophore,
            acceptor_fluorophore=acceptor_fluorophore,
            forster_radius_angstrom=forster_radius_angstrom,
            acquisition_rate_hz=acquisition_rate_hz,
            total_molecules_recorded=total_molecules_recorded,
            state_count=state_count,
            experiment_metadata_json=experiment_metadata_json or {},
        )
        self.session.add(exp)
        await self.session.commit()
        await self.session.refresh(exp)
        return exp

    async def get_experiment(self, experiment_id: str) -> Optional[DBSmFRETExperiment]:
        stmt = select(DBSmFRETExperiment).where(DBSmFRETExperiment.id == experiment_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_experiments(self, limit: int = 50, offset: int = 0) -> List[DBSmFRETExperiment]:
        stmt = select(DBSmFRETExperiment).order_by(desc(DBSmFRETExperiment.created_at)).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_traces(
        self,
        experiment_id: str,
        traces_data: List[Dict[str, Any]],
    ) -> List[DBSmFRETMoleculeTrace]:
        created = []
        for t in traces_data:
            item = DBSmFRETMoleculeTrace(
                experiment_id=experiment_id,
                molecule_index=t["molecule_index"],
                total_frames=t.get("total_frames", 500),
                mean_fret_efficiency=t.get("mean_fret_efficiency", 0.5),
                photobleaching_frame=t.get("photobleaching_frame"),
                trace_data_json=t.get("trace_data_json", []),
            )
            self.session.add(item)
            created.append(item)
        await self.session.commit()
        for item in created:
            await self.session.refresh(item)
        return created

    async def get_traces_by_experiment(self, experiment_id: str) -> List[DBSmFRETMoleculeTrace]:
        stmt = select(DBSmFRETMoleculeTrace).where(DBSmFRETMoleculeTrace.experiment_id == experiment_id).order_by(DBSmFRETMoleculeTrace.molecule_index)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_states(
        self,
        experiment_id: str,
        states_data: List[Dict[str, Any]],
    ) -> List[DBConformationalState]:
        created = []
        for s in states_data:
            item = DBConformationalState(
                experiment_id=experiment_id,
                state_index=s["state_index"],
                state_name=s["state_name"],
                mean_efficiency=s["mean_efficiency"],
                occupancy_fraction=s["occupancy_fraction"],
                mean_dwell_time_ms=s["mean_dwell_time_ms"],
                transition_rates_json=s.get("transition_rates_json", {}),
            )
            self.session.add(item)
            created.append(item)
        await self.session.commit()
        for item in created:
            await self.session.refresh(item)
        return created

    async def get_states_by_experiment(self, experiment_id: str) -> List[DBConformationalState]:
        stmt = select(DBConformationalState).where(DBConformationalState.experiment_id == experiment_id).order_by(DBConformationalState.state_index)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
