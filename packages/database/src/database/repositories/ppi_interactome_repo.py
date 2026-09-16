"""
Repository for Protein-Protein Interaction (PPI) Interactome (Phase 58).
"""
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.ppi_interactome import (
    DBPPIInteractomeNetwork,
    DBProteinNode,
    DBProteinInteractionEdge,
)


class PPIInteractomeRepository:
    """Handles CRUD operations for PPI networks, protein nodes, and interaction edges."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_network(
        self,
        network_name: str,
        disease_context: str,
        metadata_info: Optional[Dict[str, Any]] = None,
    ) -> DBPPIInteractomeNetwork:
        net = DBPPIInteractomeNetwork(
            id=str(uuid.uuid4()),
            network_name=network_name,
            disease_context=disease_context,
            metadata_info=metadata_info or {},
        )
        self.session.add(net)
        await self.session.flush()
        await self.session.commit()
        return net

    async def add_nodes_and_edges(
        self,
        network_id: str,
        nodes_data: List[Dict[str, Any]],
        edges_data: List[Dict[str, Any]],
    ) -> DBPPIInteractomeNetwork:
        for n in nodes_data:
            node = DBProteinNode(
                id=str(uuid.uuid4()),
                network_id=network_id,
                gene_symbol=n["gene_symbol"],
                uniprot_id=n.get("uniprot_id", "P00000"),
                degree_centrality=n.get("degree_centrality", 0.5),
                betweenness_centrality=n.get("betweenness_centrality", 0.3),
                is_hub_target=n.get("is_hub_target", False),
            )
            self.session.add(node)

        for e in edges_data:
            edge = DBProteinInteractionEdge(
                id=str(uuid.uuid4()),
                network_id=network_id,
                source_protein=e["source_protein"],
                target_protein=e["target_protein"],
                interaction_type=e.get("interaction_type", "Physical Binding"),
                binding_affinity_kd_nm=e.get("binding_affinity_kd_nm", 50.0),
                confidence_score=e.get("confidence_score", 0.9),
                druggability_index=e.get("druggability_index", 0.8),
                interface_surface_area_a2=e.get("interface_surface_area_a2", 1450.0),
            )
            self.session.add(edge)

        await self.session.flush()

        net = await self.get_network(network_id)
        if net:
            net.total_nodes = len(nodes_data)
            net.total_edges = len(edges_data)
            self.session.add(net)

        await self.session.commit()
        return net

    async def get_network(self, network_id: str) -> Optional[DBPPIInteractomeNetwork]:
        self.session.expire_all()
        query = (
            select(DBPPIInteractomeNetwork)
            .options(
                selectinload(DBPPIInteractomeNetwork.nodes),
                selectinload(DBPPIInteractomeNetwork.edges),
            )
            .where(DBPPIInteractomeNetwork.id == network_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_networks(self, limit: int = 50) -> List[DBPPIInteractomeNetwork]:
        query = (
            select(DBPPIInteractomeNetwork)
            .options(selectinload(DBPPIInteractomeNetwork.nodes))
            .order_by(desc(DBPPIInteractomeNetwork.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
