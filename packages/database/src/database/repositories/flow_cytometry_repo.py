from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from database.models.flow_cytometry import (
    DBFlowCytometryExperiment,
    DBBivariateGatingHierarchy,
    DBAssayZPrimeMetric,
)

class FlowCytometryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_experiment(
        self,
        experiment_name: str,
        sample_id: str,
        cell_type: str = "PBMC",
        panel_markers: Optional[List[str]] = None,
        fcs_file_path: Optional[str] = None,
        total_event_count: int = 50000,
        properties: Optional[Dict[str, Any]] = None,
    ) -> DBFlowCytometryExperiment:
        exp = DBFlowCytometryExperiment(
            experiment_name=experiment_name,
            sample_id=sample_id,
            cell_type=cell_type,
            panel_markers=panel_markers or ["FSC", "SSC", "CD3-FITC", "CD4-PE", "CD8-APC"],
            fcs_file_path=fcs_file_path,
            total_event_count=total_event_count,
            properties=properties or {},
        )
        self.session.add(exp)
        await self.session.commit()
        await self.session.refresh(exp)
        return exp

    async def add_gating_step(
        self,
        experiment_id: str,
        gate_name: str,
        x_channel: str,
        y_channel: str,
        polygon_vertices_json: List[List[float]],
        gated_event_count: int,
        population_pct_of_parent: float,
        population_pct_of_total: float,
        parent_gate_id: Optional[str] = None,
    ) -> DBBivariateGatingHierarchy:
        gate = DBBivariateGatingHierarchy(
            experiment_id=experiment_id,
            gate_name=gate_name,
            parent_gate_id=parent_gate_id,
            x_channel=x_channel,
            y_channel=y_channel,
            polygon_vertices_json=polygon_vertices_json,
            gated_event_count=gated_event_count,
            population_pct_of_parent=population_pct_of_parent,
            population_pct_of_total=population_pct_of_total,
        )
        self.session.add(gate)
        await self.session.commit()
        await self.session.refresh(gate)
        return gate

    async def add_z_prime_metric(
        self,
        experiment_id: str,
        plate_id: str,
        positive_control_mean: float,
        positive_control_sd: float,
        negative_control_mean: float,
        negative_control_sd: float,
        z_prime_factor: float,
        assay_quality_status: str,
        signal_to_background: float = 12.5,
    ) -> DBAssayZPrimeMetric:
        metric = DBAssayZPrimeMetric(
            experiment_id=experiment_id,
            plate_id=plate_id,
            positive_control_mean=positive_control_mean,
            positive_control_sd=positive_control_sd,
            negative_control_mean=negative_control_mean,
            negative_control_sd=negative_control_sd,
            z_prime_factor=z_prime_factor,
            assay_quality_status=assay_quality_status,
            signal_to_background=signal_to_background,
        )
        self.session.add(metric)
        await self.session.commit()
        await self.session.refresh(metric)
        return metric

    async def get_experiment_by_id(self, experiment_id: str) -> Optional[DBFlowCytometryExperiment]:
        stmt = (
            select(DBFlowCytometryExperiment)
            .options(
                selectinload(DBFlowCytometryExperiment.gates),
                selectinload(DBFlowCytometryExperiment.z_prime_metrics),
            )
            .where(DBFlowCytometryExperiment.id == experiment_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_experiments(self, limit: int = 50) -> List[DBFlowCytometryExperiment]:
        stmt = (
            select(DBFlowCytometryExperiment)
            .options(
                selectinload(DBFlowCytometryExperiment.gates),
                selectinload(DBFlowCytometryExperiment.z_prime_metrics),
            )
            .order_by(DBFlowCytometryExperiment.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
