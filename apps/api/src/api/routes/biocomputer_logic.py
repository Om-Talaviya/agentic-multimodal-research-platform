"""
Phase 131: Synthetic Gene Logic Biocomputer & Multi-Input Cellular State Classifier API Routes.
"""

from typing import Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from database.repositories.biocomputer_logic_repo import BiocomputerLogicRepository
from research.synthetic.biocomputer_logic_engine import (
    BiocomputerLogicEngine,
    BiomarkerThreshold,
)

router = APIRouter(prefix="/biocomputer-logic", tags=["Phase 131: Biocomputer Gene Logic Circuits"])


class MarkerInput(BaseModel):
    marker_name: str
    target_state: bool = True
    threshold_rfu: float = 1000.0


class RunCircuitSimulationRequest(BaseModel):
    circuit_name: str = Field(..., example="Glioblastoma_MultiInput_Biocomputer")
    target_cell_type: str = Field(..., example="Glioblastoma Multiforme (GBM)")
    logic_expression: str = Field("(miR-21 AND NOT miR-141) AND (EGFRvIII OR Myc)", example="(miR-21 AND NOT miR-141) AND (EGFRvIII OR Myc)")
    output_payload: str = Field("tBid_Apoptosis_Inducer", example="tBid_Apoptosis_Inducer")
    biomarkers: List[MarkerInput] = Field(default_factory=list)
    project_id: Optional[str] = Field(None)


@router.post("/simulate", status_code=status.HTTP_201_CREATED)
async def simulate_biocomputer_circuit(
    req: RunCircuitSimulationRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Execute digital gene circuit logic evaluation, compute truth table, and persist circuit."""
    markers_spec = [
        BiomarkerThreshold(
            marker_name=m.marker_name,
            target_state=m.target_state,
            threshold_rfu=m.threshold_rfu,
        )
        for m in req.biomarkers
    ] if req.biomarkers else [
        BiomarkerThreshold(marker_name="miR-21", target_state=True, threshold_rfu=1500.0),
        BiomarkerThreshold(marker_name="miR-141", target_state=False, threshold_rfu=800.0),
        BiomarkerThreshold(marker_name="EGFRvIII", target_state=True, threshold_rfu=2200.0),
        BiomarkerThreshold(marker_name="Myc", target_state=True, threshold_rfu=3100.0),
    ]

    engine = BiocomputerLogicEngine()
    sim_res = engine.simulate_circuit(
        circuit_name=req.circuit_name,
        target_cell_type=req.target_cell_type,
        biomarkers=markers_spec,
        logic_expression=req.logic_expression,
        payload=req.output_payload,
    )

    repo = BiocomputerLogicRepository(db)
    circuit = await repo.create_circuit(
        circuit_name=req.circuit_name,
        target_cell_type=req.target_cell_type,
        logic_expression=req.logic_expression,
        truth_table=sim_res.truth_table,
        gate_count=len(sim_res.gates),
        noise_margin_db=sim_res.noise_margin_db,
        metadata_json={
            "classifier_metrics": sim_res.classifier_metrics,
            "transfer_curve": sim_res.signal_transfer_curve,
        },
        project_id=req.project_id,
    )

    for g in sim_res.gates:
        await repo.add_logic_gate(
            circuit_id=circuit.id,
            gate_id=g["gate_id"],
            gate_type=g["gate_type"],
            promoter_repressor_pair=g["promoter_repressor_pair"],
            km_uM=g["km_uM"],
            hill_n=g["hill_n"],
            signal_delay_mins=g["signal_delay_mins"],
            state_high_output_rfu=g["state_high_output_rfu"],
            state_low_output_rfu=g["state_low_output_rfu"],
        )

    await repo.add_classifier(
        circuit_id=circuit.id,
        classifier_name=f"{req.circuit_name}_StateClassifier",
        input_biomarkers=[m.marker_name for m in markers_spec],
        output_payload=req.output_payload,
        classification_accuracy=sim_res.classifier_metrics["classification_accuracy"],
        false_positive_rate=sim_res.classifier_metrics["false_positive_rate"],
        auc_roc=sim_res.classifier_metrics["auc_roc"],
    )

    return {
        "status": "success",
        "circuit_id": str(circuit.id),
        "circuit_name": circuit.circuit_name,
        "gates_count": len(sim_res.gates),
        "truth_table_states": sim_res.truth_table["total_states"],
        "classifier_metrics": sim_res.classifier_metrics,
        "noise_margin_db": sim_res.noise_margin_db,
        "recommendations": sim_res.recommendations,
    }


@router.get("/circuits", response_model=List[Dict[str, Any]])
async def list_circuits(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List all registered biocomputer logic circuits."""
    repo = BiocomputerLogicRepository(db)
    circuits = await repo.list_circuits(limit=limit, offset=offset)
    return [
        {
            "id": str(c.id),
            "circuit_name": c.circuit_name,
            "target_cell_type": c.target_cell_type,
            "logic_expression": c.logic_expression,
            "gate_count": c.gate_count,
            "noise_margin_db": c.noise_margin_db,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in circuits
    ]


@router.get("/circuits/{circuit_id}")
async def get_circuit_details(
    circuit_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get full biocomputer circuit details including gates and classifier profiles."""
    repo = BiocomputerLogicRepository(db)
    circuit = await repo.get_circuit(circuit_id)
    if not circuit:
        raise HTTPException(status_code=404, detail="Biocomputer circuit not found")

    return {
        "id": str(circuit.id),
        "circuit_name": circuit.circuit_name,
        "target_cell_type": circuit.target_cell_type,
        "logic_expression": circuit.logic_expression,
        "truth_table": circuit.truth_table,
        "gate_count": circuit.gate_count,
        "noise_margin_db": circuit.noise_margin_db,
        "metadata_json": circuit.metadata_json,
        "created_at": circuit.created_at.isoformat() if circuit.created_at else None,
        "gates": [
            {
                "id": str(g.id),
                "gate_id": g.gate_id,
                "gate_type": g.gate_type,
                "promoter_repressor_pair": g.promoter_repressor_pair,
                "km_uM": g.km_uM,
                "hill_n": g.hill_n,
                "signal_delay_mins": g.signal_delay_mins,
                "state_high_output_rfu": g.state_high_output_rfu,
                "state_low_output_rfu": g.state_low_output_rfu,
            }
            for g in circuit.gates
        ],
        "classifiers": [
            {
                "id": str(c.id),
                "classifier_name": c.classifier_name,
                "input_biomarkers": c.input_biomarkers,
                "output_payload": c.output_payload,
                "classification_accuracy": c.classification_accuracy,
                "false_positive_rate": c.false_positive_rate,
                "auc_roc": c.auc_roc,
            }
            for c in circuit.classifiers
        ],
    }
