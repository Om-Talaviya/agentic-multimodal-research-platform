"""Repository for Phase 567: Autonomous Synthetic Protocellular Droplet-Interface-Bilayer (DIB) Ion Channel Network Communicator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.droplet_interface_bilayer_ion_network import (
    DropletInterfaceBilayerIonNetworkStudy,
    DropletInterfaceBilayerIonNetworkItemProfile,
    DropletInterfaceBilayerIonNetworkMetricTrace,
)


class DropletInterfaceBilayerIonNetworkRepository:
    """Database operations for Autonomous Synthetic Protocellular Droplet-Interface-Bilayer (DIB) Ion Channel Network Communicator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Aqueous Microdroplets in Oil with Encapsulated Alpha-Hemolysin Ion Channels arranged in a 3D Interfacial Bio-Conductive Lattice",
        analytical_modality: str = "droplet-interface-bilayer-network",
        interfacial_bilayer_electrical_capacitance_uf_cm2: float = 0.72,
        single_channel_conductance_quantization_ps: float = 980.0,
        inter_droplet_signal_transmission_speed_mm_s: float = 2.8,
        multi_nodal_droplet_network_stability_hours: float = 96.0,
        confidence_score: float = 0.995,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> DropletInterfaceBilayerIonNetworkStudy:
        study = DropletInterfaceBilayerIonNetworkStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            interfacial_bilayer_electrical_capacitance_uf_cm2=interfacial_bilayer_electrical_capacitance_uf_cm2,
            single_channel_conductance_quantization_ps=single_channel_conductance_quantization_ps,
            inter_droplet_signal_transmission_speed_mm_s=inter_droplet_signal_transmission_speed_mm_s,
            multi_nodal_droplet_network_stability_hours=multi_nodal_droplet_network_stability_hours,
            confidence_score=confidence_score,
            status=status,
            parameters=parameters or {},
            summary_report=summary_report,
        )
        self.session.add(study)
        await self.session.flush()
        await self.session.refresh(study)
        return study

    async def add_item_profile(
        self,
        study_id: UUID,
        item_name: str,
        profile_category: str = "Analysis Profile",
        quantitative_value: float = 1.0,
        log2_fold_change: float = 1.5,
        significance_score: float = 0.95,
    ) -> DropletInterfaceBilayerIonNetworkItemProfile:
        item = DropletInterfaceBilayerIonNetworkItemProfile(
            study_id=study_id,
            item_name=item_name,
            profile_category=profile_category,
            quantitative_value=quantitative_value,
            log2_fold_change=log2_fold_change,
            significance_score=significance_score,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def add_metric_trace(
        self,
        study_id: UUID,
        metric_dimension: str,
        observed_value: float,
        z_score: float = 0.0,
        p_value: float = 0.05,
    ) -> DropletInterfaceBilayerIonNetworkMetricTrace:
        trace = DropletInterfaceBilayerIonNetworkMetricTrace(
            study_id=study_id,
            metric_dimension=metric_dimension,
            observed_value=observed_value,
            z_score=z_score,
            p_value=p_value,
        )
        self.session.add(trace)
        await self.session.flush()
        await self.session.refresh(trace)
        return trace

    async def get_study(self, study_id: UUID) -> Optional[DropletInterfaceBilayerIonNetworkStudy]:
        stmt = (
            select(DropletInterfaceBilayerIonNetworkStudy)
            .where(DropletInterfaceBilayerIonNetworkStudy.id == study_id)
            .options(
                selectinload(DropletInterfaceBilayerIonNetworkStudy.item_profiles),
                selectinload(DropletInterfaceBilayerIonNetworkStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[DropletInterfaceBilayerIonNetworkStudy]:
        stmt = (
            select(DropletInterfaceBilayerIonNetworkStudy)
            .order_by(DropletInterfaceBilayerIonNetworkStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(DropletInterfaceBilayerIonNetworkStudy.item_profiles),
                selectinload(DropletInterfaceBilayerIonNetworkStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
