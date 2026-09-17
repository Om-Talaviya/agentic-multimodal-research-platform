from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.flow_cytometry_repo import FlowCytometryRepository
from research.flow_cytometry.flow_cytometry_engine import FlowCytometryGatingEngine

router = APIRouter(prefix="/api/v1/flow-cytometry", tags=["Flow Cytometry & HTS Robotics"])

class GatingStepInput(BaseModel):
    gate_name: str = Field(..., example="Lymphocytes")
    x_channel: str = Field("FSC-A", example="FSC-A")
    y_channel: str = Field("SSC-A", example="SSC-A")
    polygon_vertices: List[List[float]] = Field(default_factory=lambda: [[20000, 10000], [60000, 10000], [60000, 50000], [20000, 50000]])
    synthetic_retention_rate: float = Field(0.78, example=0.78)

class FlowCytometryAnalyzeRequest(BaseModel):
    experiment_name: str = Field(..., example="CAR-T CD4/CD8 Expansion Assay")
    sample_id: str = Field(..., example="SMP-FLOW-4401")
    cell_type: str = Field("CAR-T", example="CAR-T")
    panel_markers: List[str] = Field(default_factory=lambda: ["FSC-A", "SSC-A", "CD3-FITC", "CD4-PE", "CD8-APC", "Live/Dead-eFluor780"])
    total_event_count: int = Field(50000, example=50000)
    gating_steps: List[GatingStepInput]
    positive_controls: List[float] = Field(default_factory=lambda: [94.2, 95.1, 93.8, 96.0, 94.7])
    negative_controls: List[float] = Field(default_factory=lambda: [4.1, 3.8, 4.5, 3.9, 4.2])
    plate_id: str = Field("PLT-384-HTS-01", example="PLT-384-HTS-01")

@router.post("/analyze", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def analyze_flow_cytometry_run(
    request: FlowCytometryAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Autonomous Flow Cytometry Bivariate Gating & HTS Robotics Z'-factor Quality Screen.
    """
    engine = FlowCytometryGatingEngine()
    repo = FlowCytometryRepository(db)

    # 1. Create experiment record
    exp = await repo.create_experiment(
        experiment_name=request.experiment_name,
        sample_id=request.sample_id,
        cell_type=request.cell_type,
        panel_markers=request.panel_markers,
        total_event_count=request.total_event_count,
    )

    # 2. Execute hierarchical gating
    steps_payload = [step.dict() for step in request.gating_steps]
    gated_results = engine.execute_hierarchical_gating(
        total_event_count=request.total_event_count,
        gating_steps=steps_payload,
    )

    # 3. Persist gating hierarchy
    parent_id = None
    for res in gated_results:
        gate_db = await repo.add_gating_step(
            experiment_id=exp.id,
            gate_name=res["gate_name"],
            x_channel=res["x_channel"],
            y_channel=res["y_channel"],
            polygon_vertices_json=res["polygon_vertices"],
            gated_event_count=res["gated_event_count"],
            population_pct_of_parent=res["population_pct_of_parent"],
            population_pct_of_total=res["population_pct_of_total"],
            parent_gate_id=parent_id,
        )
        parent_id = gate_db.id

    # 4. Calculate Z'-Factor for HTS QC
    zprime = engine.calculate_z_prime_factor(
        positive_control_values=request.positive_controls,
        negative_control_values=request.negative_controls,
    )

    # 5. Persist Z'-Factor metric
    await repo.add_z_prime_metric(
        experiment_id=exp.id,
        plate_id=request.plate_id,
        positive_control_mean=zprime["positive_mean"],
        positive_control_sd=zprime["positive_sd"],
        negative_control_mean=zprime["negative_mean"],
        negative_control_sd=zprime["negative_sd"],
        z_prime_factor=zprime["z_prime_factor"],
        assay_quality_status=zprime["assay_quality_status"],
        signal_to_background=zprime["signal_to_background"],
    )

    hydrated = await repo.get_experiment_by_id(exp.id)

    return {
        "status": "SUCCESS",
        "experiment_id": hydrated.id,
        "experiment_name": hydrated.experiment_name,
        "sample_id": hydrated.sample_id,
        "total_event_count": hydrated.total_event_count,
        "z_prime_factor": zprime["z_prime_factor"],
        "assay_quality_status": zprime["assay_quality_status"],
        "signal_to_background": zprime["signal_to_background"],
        "gating_hierarchy": [
            {
                "id": g.id,
                "gate_name": g.gate_name,
                "x_channel": g.x_channel,
                "y_channel": g.y_channel,
                "gated_event_count": g.gated_event_count,
                "population_pct_of_parent": g.population_pct_of_parent,
                "population_pct_of_total": g.population_pct_of_total,
            }
            for g in hydrated.gates
        ],
    }

@router.get("/experiments", response_model=List[Dict[str, Any]])
async def list_flow_cytometry_experiments(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    repo = FlowCytometryRepository(db)
    exps = await repo.list_experiments(limit=limit)
    return [
        {
            "id": e.id,
            "experiment_name": e.experiment_name,
            "sample_id": e.sample_id,
            "cell_type": e.cell_type,
            "total_event_count": e.total_event_count,
            "gates_count": len(e.gates),
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in exps
    ]

@router.get("/experiments/{experiment_id}", response_model=Dict[str, Any])
async def get_flow_cytometry_experiment(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    repo = FlowCytometryRepository(db)
    e = await repo.get_experiment_by_id(experiment_id)
    if not e:
        raise HTTPException(status_code=404, detail="Flow cytometry experiment not found")
    return {
        "id": e.id,
        "experiment_name": e.experiment_name,
        "sample_id": e.sample_id,
        "cell_type": e.cell_type,
        "panel_markers": e.panel_markers,
        "total_event_count": e.total_event_count,
        "gates": [
            {
                "id": g.id,
                "gate_name": g.gate_name,
                "parent_gate_id": g.parent_gate_id,
                "x_channel": g.x_channel,
                "y_channel": g.y_channel,
                "gated_event_count": g.gated_event_count,
                "population_pct_of_parent": g.population_pct_of_parent,
                "population_pct_of_total": g.population_pct_of_total,
            }
            for g in e.gates
        ],
        "z_prime_metrics": [
            {
                "plate_id": z.plate_id,
                "z_prime_factor": z.z_prime_factor,
                "assay_quality_status": z.assay_quality_status,
                "signal_to_background": z.signal_to_background,
            }
            for z in e.z_prime_metrics
        ],
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }
