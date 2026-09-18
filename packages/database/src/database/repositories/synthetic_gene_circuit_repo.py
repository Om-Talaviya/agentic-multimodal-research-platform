"""Repository for Synthetic Gene Circuits & Bio Logic Gates."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from database.models.synthetic_gene_circuit import (
    DBSyntheticGeneCircuit,
    DBBioLogicGate,
    DBCircuitKineticsTrace,
)


class SyntheticGeneCircuitRepository:
    """Repository handling CRUD operations for Bio Logic Circuits and Kinetics simulations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_circuit(
        self,
        workspace_id: UUID,
        circuit_name: str,
        logic_function: str = "AND",
        chassis_organism: str = "Escherichia coli K-12",
        input_signals: Optional[List[str]] = None,
        output_reporter: str = "sfGFP",
        assembly_standard: str = "Golden Gate (MoClo)",
        plasmid_size_bp: int = 5400,
        on_off_dynamic_range: float = 12.5,
        circuit_metadata: Optional[Dict[str, Any]] = None,
    ) -> DBSyntheticGeneCircuit:
        circuit = DBSyntheticGeneCircuit(
            workspace_id=workspace_id,
            circuit_name=circuit_name,
            logic_function=logic_function,
            chassis_organism=chassis_organism,
            input_signals=input_signals or ["InputA", "InputB"],
            output_reporter=output_reporter,
            assembly_standard=assembly_standard,
            plasmid_size_bp=plasmid_size_bp,
            on_off_dynamic_range=on_off_dynamic_range,
            circuit_metadata=circuit_metadata or {},
        )
        self.session.add(circuit)
        await self.session.commit()
        await self.session.refresh(circuit)
        return circuit

    async def get_circuit(self, circuit_id: UUID) -> Optional[DBSyntheticGeneCircuit]:
        query = (
            select(DBSyntheticGeneCircuit)
            .where(DBSyntheticGeneCircuit.id == circuit_id)
            .options(
                selectinload(DBSyntheticGeneCircuit.gates),
                selectinload(DBSyntheticGeneCircuit.kinetics_traces),
            )
        )
        res = await self.session.execute(query)
        return res.scalars().first()

    async def list_circuits(self, workspace_id: UUID, limit: int = 50, offset: int = 0) -> List[DBSyntheticGeneCircuit]:
        query = (
            select(DBSyntheticGeneCircuit)
            .where(DBSyntheticGeneCircuit.workspace_id == workspace_id)
            .order_by(desc(DBSyntheticGeneCircuit.created_at))
            .limit(limit)
            .offset(offset)
        )
        res = await self.session.execute(query)
        return list(res.scalars().all())

    async def add_gate(
        self,
        circuit_id: UUID,
        gate_name: str,
        gate_type: str,
        promoter_part: str,
        repressor_activator: str,
        rbs_strength: float = 1.0,
        hill_coefficient_n: float = 2.2,
        kd_dissociation_uM: float = 0.15,
        overhang_5p: str = "AATG",
        overhang_3p: str = "AGCT",
    ) -> DBBioLogicGate:
        gate = DBBioLogicGate(
            circuit_id=circuit_id,
            gate_name=gate_name,
            gate_type=gate_type,
            promoter_part=promoter_part,
            repressor_activator=repressor_activator,
            rbs_strength=rbs_strength,
            hill_coefficient_n=hill_coefficient_n,
            kd_dissociation_uM=kd_dissociation_uM,
            overhang_5p=overhang_5p,
            overhang_3p=overhang_3p,
        )
        self.session.add(gate)
        await self.session.commit()
        await self.session.refresh(gate)
        return gate

    async def add_kinetics_trace(
        self,
        circuit_id: UUID,
        state_condition: str,
        simulation_duration_min: float,
        steady_state_expression_au: float,
        response_half_time_min: float = 45.0,
        time_series_data: Optional[List[Dict[str, float]]] = None,
    ) -> DBCircuitKineticsTrace:
        trace = DBCircuitKineticsTrace(
            circuit_id=circuit_id,
            state_condition=state_condition,
            simulation_duration_min=simulation_duration_min,
            steady_state_expression_au=steady_state_expression_au,
            response_half_time_min=response_half_time_min,
            time_series_data=time_series_data or [],
        )
        self.session.add(trace)
        await self.session.commit()
        await self.session.refresh(trace)
        return trace
