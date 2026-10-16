"""FastAPI routes for Phase 567: Autonomous Synthetic Protocellular Droplet-Interface-Bilayer (DIB) Ion Channel Network Communicator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.droplet_interface_bilayer_ion_network_repo import DropletInterfaceBilayerIonNetworkRepository
from research.orchestration.droplet_interface_bilayer_ion_network_engine import DropletInterfaceBilayerIonNetworkEngine

router = APIRouter(prefix="/droplet-interface-bilayer-ion-network", tags=["droplet-interface-bilayer-ion-network"])


class AnalyzeDropletInterfaceBilayerIonNetworkRequest(BaseModel):
    name: str = Field(..., example="Autonomous Synthetic Protocellular Droplet-Interface-Bilayer (DIB) Ion Channel Network Communicator Run")
    target_specimen: str = Field(default="Aqueous Microdroplets in Oil with Encapsulated Alpha-Hemolysin Ion Channels arranged in a 3D Interfacial Bio-Conductive Lattice")
    analytical_modality: str = Field(default="droplet-interface-bilayer-network")
    input_scale: float = Field(default=1.0, ge=0.1, le=100.0)


class ItemProfileResponse(BaseModel):
    item_name: str
    profile_category: str
    quantitative_value: float
    log2_fold_change: float
    significance_score: float


class MetricTraceResponse(BaseModel):
    metric_dimension: str
    observed_value: float
    z_score: float
    p_value: float


class DropletInterfaceBilayerIonNetworkStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    interfacial_bilayer_electrical_capacitance_uf_cm2: float
    single_channel_conductance_quantization_ps: float
    inter_droplet_signal_transmission_speed_mm_s: float
    multi_nodal_droplet_network_stability_hours: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=DropletInterfaceBilayerIonNetworkStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_droplet_interface_bilayer_ion_network(
    req: AnalyzeDropletInterfaceBilayerIonNetworkRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Synthetic Protocellular Droplet-Interface-Bilayer (DIB) Ion Channel Network Communicator analysis and persist study."""
    engine = DropletInterfaceBilayerIonNetworkEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = DropletInterfaceBilayerIonNetworkRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        interfacial_bilayer_electrical_capacitance_uf_cm2=result.interfacial_bilayer_electrical_capacitance_uf_cm2,
        single_channel_conductance_quantization_ps=result.single_channel_conductance_quantization_ps,
        inter_droplet_signal_transmission_speed_mm_s=result.inter_droplet_signal_transmission_speed_mm_s,
        multi_nodal_droplet_network_stability_hours=result.multi_nodal_droplet_network_stability_hours,
        confidence_score=result.confidence_score,
        status="completed",
        summary_report=result.summary_report,
    )

    for item in result.item_profiles:
        await repo.add_item_profile(
            study_id=study.id,
            item_name=item.item_name,
            profile_category=item.profile_category,
            quantitative_value=item.quantitative_value,
            log2_fold_change=item.log2_fold_change,
            significance_score=item.significance_score,
        )

    for trace in result.metric_traces:
        await repo.add_metric_trace(
            study_id=study.id,
            metric_dimension=trace.metric_dimension,
            observed_value=trace.observed_value,
            z_score=trace.z_score,
            p_value=trace.p_value,
        )

    return DropletInterfaceBilayerIonNetworkStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        interfacial_bilayer_electrical_capacitance_uf_cm2=study.interfacial_bilayer_electrical_capacitance_uf_cm2,
        single_channel_conductance_quantization_ps=study.single_channel_conductance_quantization_ps,
        inter_droplet_signal_transmission_speed_mm_s=study.inter_droplet_signal_transmission_speed_mm_s,
        multi_nodal_droplet_network_stability_hours=study.multi_nodal_droplet_network_stability_hours,
        confidence_score=study.confidence_score,
        status=study.status,
        summary_report=study.summary_report,
        item_profiles=[
            ItemProfileResponse(
                item_name=it.item_name,
                profile_category=it.profile_category,
                quantitative_value=it.quantitative_value,
                log2_fold_change=it.log2_fold_change,
                significance_score=it.significance_score,
            ) for it in result.item_profiles
        ],
        metric_traces=[
            MetricTraceResponse(
                metric_dimension=tr.metric_dimension,
                observed_value=tr.observed_value,
                z_score=tr.z_score,
                p_value=tr.p_value,
            ) for tr in result.metric_traces
        ],
    )


@router.get("/studies", response_model=List[DropletInterfaceBilayerIonNetworkStudyResponse])
async def list_droplet_interface_bilayer_ion_network_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Synthetic Protocellular Droplet-Interface-Bilayer (DIB) Ion Channel Network Communicator studies."""
    repo = DropletInterfaceBilayerIonNetworkRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=DropletInterfaceBilayerIonNetworkStudyResponse)
async def get_droplet_interface_bilayer_ion_network_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Synthetic Protocellular Droplet-Interface-Bilayer (DIB) Ion Channel Network Communicator study by ID."""
    repo = DropletInterfaceBilayerIonNetworkRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
