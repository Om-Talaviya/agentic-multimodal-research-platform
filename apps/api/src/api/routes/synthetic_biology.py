"""
FastAPI router for Synthetic Biology DNA Circuit Design (Phase 65).
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session
from database.repositories.synthetic_biology_repo import SyntheticBiologyRepository
from research.synbio.synbio_engine import SyntheticBiologyEngine

router = APIRouter(prefix="/synthetic-biology", tags=["Synthetic Biology"])


class CompileCircuitRequest(BaseModel):
    circuit_name: str = Field(default="Dual-Input Biosensor AND-Gate")
    host_organism: str = Field(default="E. coli K-12 (MG1655)")
    logic_expression: str = Field(default="A AND B")
    gate_topology: str = Field(default="Two-Input Transcriptional AND Gate")


@router.post("/circuits", status_code=status.HTTP_201_CREATED)
async def compile_synthetic_circuit(
    request: CompileCircuitRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Compiles high-level boolean logic into assembled DNA genetic circuit parts with truth table simulation."""
    repo = SyntheticBiologyRepository(db)
    circuit = await repo.create_circuit(
        circuit_name=request.circuit_name,
        host_organism=request.host_organism,
        logic_expression=request.logic_expression,
        gate_topology=request.gate_topology,
    )

    compiled = SyntheticBiologyEngine.compile_circuit(
        circuit_name=request.circuit_name,
        logic_expression=request.logic_expression,
        host_organism=request.host_organism,
    )

    return await repo.add_parts_and_truth_table(
        circuit_id=circuit.id,
        parts_data=compiled["parts"],
        truth_table_data=compiled["truth_table"],
        on_off_ratio=compiled["on_off_ratio"],
        sbol_xml=compiled["sbol_xml"],
    )


@router.get("/circuits")
async def list_synthetic_circuits(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
):
    """Lists compiled synthetic DNA circuits."""
    repo = SyntheticBiologyRepository(db)
    return await repo.list_circuits(limit=limit)


@router.get("/circuits/{circuit_id}")
async def get_synthetic_circuit(
    circuit_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieves full genetic circuit assembly, biological parts list, and truth table response."""
    repo = SyntheticBiologyRepository(db)
    circuit = await repo.get_circuit(circuit_id)
    if not circuit:
        raise HTTPException(status_code=404, detail="Synthetic DNA circuit not found")
    return circuit
