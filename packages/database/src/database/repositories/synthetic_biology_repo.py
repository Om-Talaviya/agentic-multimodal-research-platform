"""
Repository for Synthetic Biology DNA Circuit Design (Phase 65).
"""
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.synthetic_biology import (
    DBSyntheticCircuitDesign,
    DBGeneticPart,
    DBCircuitTruthTableEntry,
)


class SyntheticBiologyRepository:
    """Handles CRUD operations for synthetic DNA circuits, genetic parts, and truth table data."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_circuit(
        self,
        circuit_name: str,
        host_organism: str = "E. coli K-12 (MG1655)",
        logic_expression: str = "A AND B",
        gate_topology: str = "Two-Input AND Gate",
        metadata_info: Optional[Dict[str, Any]] = None,
    ) -> DBSyntheticCircuitDesign:
        circuit = DBSyntheticCircuitDesign(
            id=str(uuid.uuid4()),
            circuit_name=circuit_name,
            host_organism=host_organism,
            logic_expression=logic_expression,
            gate_topology=gate_topology,
            metadata_info=metadata_info or {},
        )
        self.session.add(circuit)
        await self.session.flush()
        await self.session.commit()
        return circuit

    async def add_parts_and_truth_table(
        self,
        circuit_id: str,
        parts_data: List[Dict[str, Any]],
        truth_table_data: List[Dict[str, Any]],
        on_off_ratio: float = 42.5,
        sbol_xml: str = "",
    ) -> DBSyntheticCircuitDesign:
        for idx, p in enumerate(parts_data):
            part = DBGeneticPart(
                id=str(uuid.uuid4()),
                circuit_id=circuit_id,
                part_type=p["part_type"],
                part_name=p["part_name"],
                part_sequence=p.get("part_sequence", "ATGCGTAGCTAG"),
                order_index=p.get("order_index", idx + 1),
                relative_strength_au=p.get("relative_strength_au", 1.0),
                repressor_affinity_kd_um=p.get("repressor_affinity_kd_um"),
            )
            self.session.add(part)

        for tt in truth_table_data:
            entry = DBCircuitTruthTableEntry(
                id=str(uuid.uuid4()),
                circuit_id=circuit_id,
                input_state_a=tt["input_state_a"],
                input_state_b=tt.get("input_state_b", False),
                expected_output=tt["expected_output"],
                simulated_fluorescence_rfu=tt["simulated_fluorescence_rfu"],
                response_delay_minutes=tt.get("response_delay_minutes", 25.0),
            )
            self.session.add(entry)

        await self.session.flush()

        circuit = await self.get_circuit(circuit_id)
        if circuit:
            circuit.total_parts = len(parts_data)
            circuit.dynamic_range_on_off_ratio = on_off_ratio
            circuit.sbol_xml_preview = sbol_xml
            self.session.add(circuit)

        await self.session.commit()
        return circuit

    async def get_circuit(self, circuit_id: str) -> Optional[DBSyntheticCircuitDesign]:
        self.session.expire_all()
        query = (
            select(DBSyntheticCircuitDesign)
            .options(
                selectinload(DBSyntheticCircuitDesign.parts),
                selectinload(DBSyntheticCircuitDesign.truth_table),
            )
            .where(DBSyntheticCircuitDesign.id == circuit_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_circuits(self, limit: int = 50) -> List[DBSyntheticCircuitDesign]:
        query = (
            select(DBSyntheticCircuitDesign)
            .options(selectinload(DBSyntheticCircuitDesign.parts))
            .order_by(desc(DBSyntheticCircuitDesign.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
