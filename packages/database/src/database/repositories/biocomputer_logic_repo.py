"""
Repository for Phase 131: Synthetic Gene Logic Biocomputer & Multi-Input Cellular State Classifier.
"""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from database.models.biocomputer_logic import (
    DBBiocomputerCircuit,
    DBLogicGateCascade,
    DBCellularStateClassifier,
)


class BiocomputerLogicRepository:
    """Repository handling CRUD operations for biocomputer circuits and logic gates."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_circuit(
        self,
        circuit_name: str,
        target_cell_type: str,
        logic_expression: str,
        truth_table: Optional[Dict[str, Any]] = None,
        gate_count: int = 4,
        noise_margin_db: float = 14.5,
        metadata_json: Optional[Dict[str, Any]] = None,
        project_id: Optional[str] = None,
    ) -> DBBiocomputerCircuit:
        """Create a new biocomputer logic circuit record."""
        circuit = DBBiocomputerCircuit(
            id=uuid.uuid4(),
            project_id=project_id,
            circuit_name=circuit_name,
            target_cell_type=target_cell_type,
            logic_expression=logic_expression,
            truth_table=truth_table or {},
            gate_count=gate_count,
            noise_margin_db=noise_margin_db,
            metadata_json=metadata_json or {},
        )
        self.session.add(circuit)
        await self.session.commit()
        await self.session.refresh(circuit)
        return circuit

    async def get_circuit(self, circuit_id: uuid.UUID) -> Optional[DBBiocomputerCircuit]:
        """Get circuit with all gates and classifiers."""
        stmt = (
            select(DBBiocomputerCircuit)
            .options(
                selectinload(DBBiocomputerCircuit.gates),
                selectinload(DBBiocomputerCircuit.classifiers),
            )
            .where(DBBiocomputerCircuit.id == circuit_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_circuits(self, limit: int = 50, offset: int = 0) -> List[DBBiocomputerCircuit]:
        """List all biocomputer circuits."""
        stmt = (
            select(DBBiocomputerCircuit)
            .order_by(desc(DBBiocomputerCircuit.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_logic_gate(
        self,
        circuit_id: uuid.UUID,
        gate_id: str,
        gate_type: str,
        promoter_repressor_pair: str,
        km_uM: float = 2.5,
        hill_n: float = 2.8,
        signal_delay_mins: float = 45.0,
        state_high_output_rfu: float = 4800.0,
        state_low_output_rfu: float = 120.0,
    ) -> DBLogicGateCascade:
        """Add a logic gate node to a circuit cascade."""
        gate = DBLogicGateCascade(
            id=uuid.uuid4(),
            circuit_id=circuit_id,
            gate_id=gate_id,
            gate_type=gate_type,
            promoter_repressor_pair=promoter_repressor_pair,
            km_uM=km_uM,
            hill_n=hill_n,
            signal_delay_mins=signal_delay_mins,
            state_high_output_rfu=state_high_output_rfu,
            state_low_output_rfu=state_low_output_rfu,
        )
        self.session.add(gate)
        await self.session.commit()
        await self.session.refresh(gate)
        return gate

    async def add_classifier(
        self,
        circuit_id: uuid.UUID,
        classifier_name: str,
        input_biomarkers: List[str],
        output_payload: str,
        classification_accuracy: float = 0.96,
        false_positive_rate: float = 0.03,
        auc_roc: float = 0.985,
    ) -> DBCellularStateClassifier:
        """Add a cellular state classifier profile to a circuit."""
        classifier = DBCellularStateClassifier(
            id=uuid.uuid4(),
            circuit_id=circuit_id,
            classifier_name=classifier_name,
            input_biomarkers=input_biomarkers,
            output_payload=output_payload,
            classification_accuracy=classification_accuracy,
            false_positive_rate=false_positive_rate,
            auc_roc=auc_roc,
        )
        self.session.add(classifier)
        await self.session.commit()
        await self.session.refresh(classifier)
        return classifier
