"""API Routes for Synthetic Biology Gene Circuit Design & Boolean Logic Synthesizer."""

import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.synthetic_gene_circuit_repo import SyntheticGeneCircuitRepository
from research.synbio.gene_circuit_engine import SyntheticGeneCircuitEngine

router = APIRouter(prefix="/synthetic-gene-circuits", tags=["Synthetic Gene Circuits & Bio Logic"])


class GeneCircuitDesignRequest(BaseModel):
    circuit_name: str = Field(..., example="CRISPR_AND_Gate_Coli")
    logic_function: str = Field(default="AND", example="AND")
    chassis_organism: str = Field(default="Escherichia coli K-12")
    output_reporter: str = Field(default="sfGFP")
    workspace_id: Optional[str] = None


@router.get("/parts")
async def get_circuit_parts_library():
    """Retrieve standard biological promoters and transcription factors."""
    return {"parts": SyntheticGeneCircuitEngine.PARTS_LIBRARY}


@router.post("/design", status_code=status.HTTP_201_CREATED)
async def design_and_simulate_circuit(
    request: GeneCircuitDesignRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Synthesize Boolean logic gate topology, simulate Hill kinetics, and compile Golden Gate plasmid."""
    engine = SyntheticGeneCircuitEngine()
    design = engine.design_logic_circuit(
        circuit_name=request.circuit_name,
        logic_function=request.logic_function,
        chassis=request.chassis_organism,
        output_reporter=request.output_reporter,
    )

    repo = SyntheticGeneCircuitRepository(db)
    ws_id = uuid.UUID(request.workspace_id) if request.workspace_id else uuid.uuid4()

    circuit = await repo.create_circuit(
        workspace_id=ws_id,
        circuit_name=design["circuit_name"],
        logic_function=design["logic_function"],
        chassis_organism=design["chassis_organism"],
        input_signals=design["input_signals"],
        output_reporter=design["output_reporter"],
        assembly_standard=design["assembly_standard"],
        plasmid_size_bp=design["plasmid_size_bp"],
        on_off_dynamic_range=design["on_off_dynamic_range"],
        circuit_metadata={"assembly_plan": design["assembly_plan"]},
    )

    for g in design["gates"]:
        await repo.add_gate(
            circuit_id=circuit.id,
            gate_name=g["gate_name"],
            gate_type=g["gate_type"],
            promoter_part=g["promoter_part"],
            repressor_activator=g["repressor_activator"],
            rbs_strength=g["rbs_strength"],
            hill_coefficient_n=g["hill_coefficient_n"],
            kd_dissociation_uM=g["kd_dissociation_uM"],
            overhang_5p=g["overhang_5p"],
            overhang_3p=g["overhang_3p"],
        )

    for t in design["kinetics_traces"]:
        await repo.add_kinetics_trace(
            circuit_id=circuit.id,
            state_condition=t["state_condition"],
            simulation_duration_min=360.0,
            steady_state_expression_au=t["steady_state_expression_au"],
            response_half_time_min=t["response_half_time_min"],
            time_series_data=t["time_series_data"],
        )

    return {
        "status": "success",
        "circuit_id": str(circuit.id),
        "circuit_name": circuit.circuit_name,
        "logic_function": circuit.logic_function,
        "chassis_organism": circuit.chassis_organism,
        "on_off_dynamic_range": circuit.on_off_dynamic_range,
        "plasmid_size_bp": circuit.plasmid_size_bp,
        "gates_count": len(design["gates"]),
        "kinetics_traces_count": len(design["kinetics_traces"]),
        "assembly_plan": design["assembly_plan"],
    }


@router.get("/circuits/{circuit_id}")
async def get_circuit_details(
    circuit_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Retrieve synthetic gene circuit details and simulation kinetics."""
    try:
        c_uuid = uuid.UUID(circuit_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid circuit UUID")

    repo = SyntheticGeneCircuitRepository(db)
    circuit = await repo.get_circuit(c_uuid)
    if not circuit:
        raise HTTPException(status_code=404, detail="Synthetic gene circuit not found")

    return {
        "id": str(circuit.id),
        "circuit_name": circuit.circuit_name,
        "logic_function": circuit.logic_function,
        "chassis_organism": circuit.chassis_organism,
        "on_off_dynamic_range": circuit.on_off_dynamic_range,
        "gates": [
            {
                "id": str(g.id),
                "gate_name": g.gate_name,
                "gate_type": g.gate_type,
                "promoter_part": g.promoter_part,
                "overhangs": f"{g.overhang_5p}-{g.overhang_3p}",
            }
            for g in circuit.gates
        ],
        "kinetics_traces": [
            {
                "id": str(kt.id),
                "state_condition": kt.state_condition,
                "steady_state_expression_au": kt.steady_state_expression_au,
                "points_count": len(kt.time_series_data),
            }
            for kt in circuit.kinetics_traces
        ],
    }
