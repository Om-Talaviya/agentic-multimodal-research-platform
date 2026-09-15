"""Spatial Transcriptomics Repository (Phase 42)."""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, delete, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.spatial_transcriptomics import (
    DBSpatialTissueDataset,
    DBCellSpatialCoordinate,
    DBCellCommunicationPair,
    DBSpatialDomain,
)

class SpatialTranscriptomicsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_dataset(
        self,
        title: str,
        tissue_type: str,
        technology: str = "10x Visium",
        organism: str = "Homo sapiens",
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
        description: Optional[str] = None,
        slide_width_um: float = 6500.0,
        slide_height_um: float = 6500.0,
        spot_diameter_um: float = 55.0,
        total_spots: int = 0,
        meta_info: Optional[Dict[str, Any]] = None,
    ) -> DBSpatialTissueDataset:
        dataset = DBSpatialTissueDataset(
            title=title,
            tissue_type=tissue_type,
            technology=technology,
            organism=organism,
            workspace_id=workspace_id,
            project_id=project_id,
            description=description,
            slide_width_um=slide_width_um,
            slide_height_um=slide_height_um,
            spot_diameter_um=spot_diameter_um,
            total_spots=total_spots,
            meta_info=meta_info or {},
        )
        self.session.add(dataset)
        await self.session.commit()
        await self.session.refresh(dataset)
        return dataset

    async def get_dataset(self, dataset_id: str) -> Optional[DBSpatialTissueDataset]:
        stmt = select(DBSpatialTissueDataset).where(DBSpatialTissueDataset.id == dataset_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_datasets(
        self,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
        tissue_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBSpatialTissueDataset]:
        stmt = select(DBSpatialTissueDataset)
        if workspace_id:
            stmt = stmt.where(DBSpatialTissueDataset.workspace_id == workspace_id)
        if project_id:
            stmt = stmt.where(DBSpatialTissueDataset.project_id == project_id)
        if tissue_type:
            stmt = stmt.where(DBSpatialTissueDataset.tissue_type.ilike(f"%{tissue_type}%"))
        stmt = stmt.order_by(desc(DBSpatialTissueDataset.created_at)).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_spots(self, dataset_id: str, spots_data: List[Dict[str, Any]]) -> int:
        spots = [
            DBCellSpatialCoordinate(
                dataset_id=dataset_id,
                spot_barcode=s["spot_barcode"],
                x_coord=s["x_coord"],
                y_coord=s["y_coord"],
                z_coord=s.get("z_coord", 0.0),
                cluster_id=s.get("cluster_id", 0),
                cluster_name=s.get("cluster_name", "Unassigned"),
                cell_type_annotation=s.get("cell_type_annotation", "Unknown"),
                total_counts=s.get("total_counts", 1000),
                n_genes_detected=s.get("n_genes_detected", 500),
                spatial_domain_id=s.get("spatial_domain_id"),
                tumor_proximity_score=s.get("tumor_proximity_score", 0.0),
                meta_info=s.get("meta_info", {}),
            )
            for s in spots_data
        ]
        self.session.add_all(spots)
        
        # update total_spots on dataset
        dataset = await self.get_dataset(dataset_id)
        if dataset:
            dataset.total_spots = len(spots)
            
        await self.session.commit()
        return len(spots)

    async def get_spots(
        self,
        dataset_id: str,
        cluster_id: Optional[int] = None,
        spatial_domain_id: Optional[str] = None,
        limit: int = 2000,
    ) -> List[DBCellSpatialCoordinate]:
        stmt = select(DBCellSpatialCoordinate).where(DBCellSpatialCoordinate.dataset_id == dataset_id)
        if cluster_id is not None:
            stmt = stmt.where(DBCellSpatialCoordinate.cluster_id == cluster_id)
        if spatial_domain_id:
            stmt = stmt.where(DBCellSpatialCoordinate.spatial_domain_id == spatial_domain_id)
        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_communications(self, dataset_id: str, comms_data: List[Dict[str, Any]]) -> int:
        comms = [
            DBCellCommunicationPair(
                dataset_id=dataset_id,
                pathway_name=c["pathway_name"],
                ligand_gene=c["ligand_gene"],
                receptor_gene=c["receptor_gene"],
                source_cluster=c["source_cluster"],
                target_cluster=c["target_cluster"],
                communication_score=c["communication_score"],
                p_value=c.get("p_value", 0.001),
                interaction_distance_um=c.get("interaction_distance_um", 120.0),
                is_spatially_constrained=c.get("is_spatially_constrained", True),
                meta_info=c.get("meta_info", {}),
            )
            for c in comms_data
        ]
        self.session.add_all(comms)
        await self.session.commit()
        return len(comms)

    async def get_communications(
        self,
        dataset_id: str,
        pathway_name: Optional[str] = None,
        min_score: float = 0.0,
    ) -> List[DBCellCommunicationPair]:
        stmt = select(DBCellCommunicationPair).where(
            DBCellCommunicationPair.dataset_id == dataset_id,
            DBCellCommunicationPair.communication_score >= min_score
        )
        if pathway_name:
            stmt = stmt.where(DBCellCommunicationPair.pathway_name == pathway_name)
        stmt = stmt.order_by(desc(DBCellCommunicationPair.communication_score))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_domains(self, dataset_id: str, domains_data: List[Dict[str, Any]]) -> int:
        domains = [
            DBSpatialDomain(
                dataset_id=dataset_id,
                domain_name=d["domain_name"],
                domain_type=d.get("domain_type", "tumor_stroma"),
                color_hex=d.get("color_hex", "#3b82f6"),
                spot_count=d.get("spot_count", 0),
                area_percentage=d.get("area_percentage", 0.0),
                top_marker_genes=d.get("top_marker_genes", []),
                boundary_polygon=d.get("boundary_polygon", []),
                meta_info=d.get("meta_info", {}),
            )
            for d in domains_data
        ]
        self.session.add_all(domains)
        await self.session.commit()
        return len(domains)

    async def get_domains(self, dataset_id: str) -> List[DBSpatialDomain]:
        stmt = select(DBSpatialDomain).where(DBSpatialDomain.dataset_id == dataset_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_dataset(self, dataset_id: str) -> bool:
        dataset = await self.get_dataset(dataset_id)
        if not dataset:
            return False
        await self.session.delete(dataset)
        await self.session.commit()
        return True
